import React, { useState, useRef, useEffect } from 'react';
import MagicBento from './MagicBento';
import StarButton from './StarButton';
import HeartbeatLoader from './HeartbeatLoader'; // Importa o novo loader

// Estilos
const cardContentStyle = { width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: '10px', color: 'white', fontSize: '14px' };
const textAreaStyle = { flexGrow: 1, width: '100%', backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'white', padding: '10px', fontFamily: 'inherit', fontSize: '14px', resize: 'none' };
const buttonStyle = { padding: '8px 12px', fontSize: '12px', color: 'var(--white)', backgroundColor: 'var(--purple-primary)', border: 'none', borderRadius: '6px', cursor: 'pointer', opacity: 1, transition: 'opacity 0.2s ease' };
const listStyle = { margin: 0, paddingLeft: '20px', fontSize: '13px', textAlign: 'left', width: '100%' };
const listItemStyle = { marginBottom: '8px' };
const strongStyle = { color: 'var(--purple-primary)' };
const scrollableTextStyle = { whiteSpace: 'pre-wrap', padding: '5px', fontSize: '13px' };

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

const ConsultationScreen = ({ userId, onFinish }) => {
    const [consulta, setConsulta] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [transcribedText, setTranscribedText] = useState('');
    const [finalNotes, setFinalNotes] = useState('');
    const [transcriptionComplete, setTranscriptionComplete] = useState(false);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const structuredNote = consulta?.sugestao_ia?.nota_clinica_estruturada || {};
    const advancedAnalysis = consulta?.sugestao_ia?.analise_clinica_avancada || {};
    
    useEffect(() => {
        const startNewConsultation = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/consulta/iniciar/${userId}`, { method: 'POST' });
                if (!response.ok) throw new Error("Falha ao contactar a API.");
                const data = await response.json();
                setConsulta(data);
            } catch (error) {
                console.error("Erro ao iniciar nova consulta:", error);
                alert("Não foi possível iniciar a consulta.");
            }
        };
        startNewConsultation();
    }, [userId]);

    const handleRecordClick = async () => {
        if (isRecording) {
            if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
                mediaRecorderRef.current.stop();
            }
            setIsRecording(false);
        } else {
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
                            const transResponse = await fetch(`${API_BASE_URL}/audio/transcrever`, { method: 'POST', body: formData });
                            if (!transResponse.ok) throw new Error('Falha na transcrição.');
                            const transData = await transResponse.json();
                            setTranscribedText(transData.texto_transcrito);
                            const payload = { consulta_atual: consulta, fala: { texto: transData.texto_transcrito } };
                            const processResponse = await fetch(`${API_BASE_URL}/consulta/processar/${userId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                            if (!processResponse.ok) throw new Error('Falha ao processar.');
                            const processData = await processResponse.json();
                            setConsulta(processData);
                            setTranscriptionComplete(true);
                        } catch (error)
                            {
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
                    alert("Não foi possível aceder ao microfone.");
                }
            }
        }
    };
    
    const handleGenerateDocument = async (docType) => {
        if (!consulta || !consulta.sugestao_ia) {
            alert("Aguarde a análise da IA.");
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
            <div style={{...cardContentStyle, justifyContent: 'center'}}>
                {isLoading ? (
                    <HeartbeatLoader />
                ) : !transcriptionComplete ? (
                    <StarButton onClick={handleRecordClick}>
                        {isRecording ? "Parar Gravação" : "Iniciar Gravação"}
                    </StarButton>
                ) : (
                    <div className="scrollable-content">
                        <p style={scrollableTextStyle}>{transcribedText}</p>
                    </div>
                )}
            </div>
        ),
        Overview: (
            <div className="scrollable-content">
                <p style={scrollableTextStyle}>{structuredNote.queixa_principal || 'Aguardando queixa principal...'}</p>
            </div>
        ),
        Efficiency: (
            <div className="scrollable-content" style={{ ...cardContentStyle, justifyContent: 'flex-start', alignItems: 'flex-start', gap: '1rem' }}>
                <div><strong style={strongStyle}>História da Doença Atual:</strong><p style={{fontSize: '13px'}}>{structuredNote.historia_doenca_atual || '...'}</p></div>
                <div><strong style={strongStyle}>Antecedentes:</strong><p style={{fontSize: '13px'}}>{structuredNote.antecedentes_pessoais_familiares || '...'}</p></div>
                <div><strong style={strongStyle}>Hipóteses Diagnósticas:</strong><ul style={listStyle}>{(structuredNote.hipoteses_diagnosticas || []).map((h, i) => <li key={i}>{h}</li>)}</ul></div>
            </div>
        ),
        Connectivity: (
            <div className="scrollable-content">
                {(advancedAnalysis.exames_complementares_sugeridos && advancedAnalysis.exames_complementares_sugeridos.length > 0) ? (
                    <ul style={listStyle}>
                        {advancedAnalysis.exames_complementares_sugeridos.map((ex, i) => (
                            <li key={i} style={listItemStyle}><strong style={strongStyle}>{ex.exame}:</strong> {ex.justificativa}</li>
                        ))}
                    </ul>
                ) : (
                    <p className="placeholder-text">Aguardando sugestões...</p>
                )}
            </div>
        ),
        Protection: (
            <div className="scrollable-content">
                 {(advancedAnalysis.sugestoes_de_tratamento && advancedAnalysis.sugestoes_de_tratamento.length > 0) ? (
                    <ul style={listStyle}>
                        {advancedAnalysis.sugestoes_de_tratamento.map((t, i) => (
                            <li key={i} style={listItemStyle}><strong style={strongStyle}>{t.medicamento_sugerido} ({t.posologia_recomendada}):</strong> {t.justificativa_clinica}</li>
                        ))}
                    </ul>
                ) : (
                    <p className="placeholder-text">Aguardando sugestões...</p>
                )}
            </div>
        ),
        Collaboration: (
            <div style={{...cardContentStyle, justifyContent: 'flex-start'}}>
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '10px' }}>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('receita')}>Gerar Receita</button>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('atestado')}>Gerar Atestado</button>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('pedido_exame')}>Pedir Exames</button>
                </div>
                <textarea 
                    style={textAreaStyle} 
                    placeholder="Escreva aqui a sua decisão final para o prontuário..."
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
                <StarButton
                  onClick={() => {
                      if (window.confirm("Tem a certeza que deseja finalizar a consulta?")) {
                          onFinish();
                      }
                  }}
                >
                  Finalizar Sessão e Salvar
                </StarButton>
            </div>
        </div>
    );
};

export default ConsultationScreen;