import React, { useState, useRef, useEffect } from 'react';
import MagicBento from './MagicBento';

// Estilos para os botões e áreas de texto
const cardContentStyle = { width: '100%', height: '100%', display: 'flex', flexDirection: 'column', gap: '10px', color: 'white', fontSize: '14px' };
const textAreaStyle = { flexGrow: 1, width: '100%', backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'white', padding: '10px', fontFamily: 'inherit', fontSize: '14px', resize: 'none' };
const buttonStyle = { padding: '8px 12px', fontSize: '12px', color: 'var(--white)', backgroundColor: 'var(--purple-primary)', border: 'none', borderRadius: '6px', cursor: 'pointer', opacity: 1, transition: 'opacity 0.2s ease' };
const buttonDisabledStyle = { ...buttonStyle, opacity: 0.5, cursor: 'not-allowed' };
const listStyle = { margin: 0, paddingLeft: '20px', fontSize: '13px' };
const listItemStyle = { marginBottom: '8px' };
const strongStyle = { color: 'var(--purple-primary)' };

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

const ConsultationScreen = ({ userId, onFinish }) => {
    // Estados para gerir a consulta
    const [consulta, setConsulta] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [transcribedText, setTranscribedText] = useState('');
    const [finalNotes, setFinalNotes] = useState('');
    const [transcriptionComplete, setTranscriptionComplete] = useState(false); // NOVO ESTADO
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    // Extrai os dados da consulta para facilitar o acesso
    const structuredNote = consulta?.sugestao_ia?.nota_clinica_estruturada || {};
    const advancedAnalysis = consulta?.sugestao_ia?.analise_clinica_avancada || {};

    // Efeito para iniciar a consulta na API quando o componente é montado
    useEffect(() => {
        const startNewConsultation = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/consulta/iniciar/${userId}`, { method: 'POST' });
                if (!response.ok) throw new Error("Falha ao contactar a API para iniciar a consulta.");
                const data = await response.json();
                setConsulta(data);
                console.log("Nova consulta iniciada:", data.id);
            } catch (error) {
                console.error("Erro ao iniciar nova consulta:", error);
                alert("Não foi possível iniciar a consulta. Verifique a conexão com a API e se ela está ativa no Render.");
            }
        };
        startNewConsultation();
    }, [userId]);

    const handleStartRecording = async () => {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorderRef.current = new MediaRecorder(stream);
                audioChunksRef.current = [];

                mediaRecorderRef.current.ondataavailable = (event) => {
                    audioChunksRef.current.push(event.data);
                };

                mediaRecorderRef.current.onstop = async () => {
                    setIsLoading(true);
                    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append("ficheiro_audio", audioBlob, "consulta.wav");

                    try {
                        // 1. Transcrever áudio
                        const transResponse = await fetch(`${API_BASE_URL}/audio/transcrever`, {
                            method: 'POST',
                            body: formData,
                        });
                        if (!transResponse.ok) throw new Error('Falha na transcrição do áudio.');
                        const transData = await transResponse.json();
                        setTranscribedText(transData.texto_transcrito);

                        // 2. Processar a fala
                        const payload = {
                            consulta_atual: consulta,
                            fala: { texto: transData.texto_transcrito }
                        };
                        const processResponse = await fetch(`${API_BASE_URL}/consulta/processar/${userId}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        if (!processResponse.ok) throw new Error('Falha ao processar a fala.');
                        const processData = await processResponse.json();
                        setConsulta(processData); // Atualiza o estado da consulta com os dados da IA
                        setTranscriptionComplete(true); // Marca a transcrição como completa

                    } catch (error) {
                        console.error("Erro no processo de gravação-análise:", error);
                        alert(`Ocorreu um erro: ${error.message}`);
                    } finally {
                        setIsLoading(false);
                    }
                };

                mediaRecorderRef.current.start();
                setIsRecording(true);
            } catch (err) {
                console.error("Erro ao obter acesso ao microfone:", err);
                alert("Não foi possível aceder ao microfone. Por favor, verifique as permissões do navegador.");
            }
        }
    };

    const handleStopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
            mediaRecorderRef.current.stop();
        }
        setIsRecording(false);
    };

    const handleGenerateDocument = async (docType) => {
        if (!consulta || !consulta.sugestao_ia) {
            alert("Aguarde a análise da IA para gerar documentos.");
            return;
        }
        alert(`A gerar ${docType}...`);
        try {
            const payload = {
                tipo_documento: docType,
                dados_consulta: consulta.sugestao_ia.nota_clinica_estruturada
            };
            const response = await fetch(`${API_BASE_URL}/consulta/gerar_documento/${userId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`Falha ao gerar ${docType}.`);
            const data = await response.json();
            
            const documentText = `\n\n--- INÍCIO ${docType.toUpperCase()} ---\n${data.documento_gerado}\n--- FIM ${docType.toUpperCase()} ---\n`;
            setFinalNotes(prevNotes => prevNotes + documentText);

        } catch (error) {
            console.error(`Erro ao gerar ${docType}:`, error);
            alert(`Ocorreu um erro: ${error.message}`);
        }
    };

    const cardContents = {
        Insights: (
            <div style={cardContentStyle}>
                {!transcriptionComplete ? (
                    <button 
                        onClick={isRecording ? handleStopRecording : handleStartRecording} 
                        disabled={isLoading}
                        style={isLoading ? buttonDisabledStyle : buttonStyle}
                    >
                        {isLoading ? "A processar..." : (isRecording ? "Parar Gravação" : "Iniciar Gravação de Voz")}
                    </button>
                ) : null}
                <textarea 
                    style={textAreaStyle} 
                    readOnly 
                    value={transcribedText || "Aguardando transcrição..."}
                >
                </textarea>
            </div>
        ),
        Overview: (
            <div style={cardContentStyle}>
                <textarea style={textAreaStyle} readOnly value={structuredNote.queixa_principal || ''}></textarea>
            </div>
        ),
        Efficiency: (
            <div style={{ ...cardContentStyle, justifyContent: 'space-around' }}>
                <div>
                    <strong style={strongStyle}>História da Doença Atual:</strong>
                    <p>{structuredNote.historia_doenca_atual || '...'}</p>
                </div>
                <div>
                    <strong style={strongStyle}>Antecedentes:</strong>
                    <p>{structuredNote.antecedentes_pessoais_familiares || '...'}</p>
                </div>
                <div>
                    <strong style={strongStyle}>Hipóteses Diagnósticas:</strong>
                    <ul style={listStyle}>
                        {(structuredNote.hipoteses_diagnosticas || []).map((h, i) => <li key={i}>{h}</li>)}
                    </ul>
                </div>
            </div>
        ),
        Connectivity: (
            <div style={cardContentStyle}>
                <ul style={listStyle}>
                    {(advancedAnalysis.exames_complementares_sugeridos || []).map((ex, i) => (
                        <li key={i} style={listItemStyle}><strong style={strongStyle}>{ex.exame}:</strong> {ex.justificativa}</li>
                    ))}
                </ul>
            </div>
        ),
        Protection: (
            <div style={cardContentStyle}>
                 <ul style={listStyle}>
                    {(advancedAnalysis.sugestoes_de_tratamento || []).map((t, i) => (
                        <li key={i} style={listItemStyle}><strong style={strongStyle}>{t.medicamento_sugerido} ({t.posologia_recomendada}):</strong> {t.justificativa_clinica}</li>
                    ))}
                </ul>
            </div>
        ),
        Collaboration: (
            <div style={cardContentStyle}>
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '10px' }}>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('receita')}>Gerar Receita</button>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('atestado')}>Gerar Atestado</button>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('pedido_exame')}>Pedir Exames</button>
                </div>
                <textarea 
                    style={textAreaStyle} 
                    placeholder="Escreva aqui o texto final para o prontuário (decisão médica)..."
                    value={finalNotes}
                    onChange={(e) => setFinalNotes(e.target.value)}
                >
                </textarea>
            </div>
        ),
    };

    return (
        <div>
            <MagicBento
              cardContents={cardContents}
              textAutoHide={false}
              enableStars={true}
              enableSpotlight={true}
              enableBorderGlow={true}
              enableTilt={true}
              enableMagnetism={true}
              clickEffect={true}
              spotlightRadius={300}
              particleCount={12}
              glowColor="132, 0, 255"
            />
            <div style={{ textAlign: 'center', padding: '1rem 0', backgroundColor: '#060010' }}>
                <button 
                  style={{
                      ...buttonStyle,
                      padding: '1rem 2rem',
                      fontSize: '1rem',
                      backgroundColor: '#d9534f',
                      boxShadow: '0 0 20px rgba(217, 83, 79, 0.4)'
                  }}
                  onClick={() => {
                      if (window.confirm("Tem a certeza que deseja finalizar a consulta?")) {
                          // Aqui chamaria a API para finalizar, por agora apenas chama a função onFinish
                          onFinish();
                      }
                  }}
                >
                  Finalizar Sessão e Salvar
                </button>
            </div>
        </div>
    );
};

export default ConsultationScreen;