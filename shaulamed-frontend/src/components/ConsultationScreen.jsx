import React, { useState, useRef, useEffect, useMemo } from 'react';
import StarButton from './StarButton';
import HeartbeatLoader from './HeartbeatLoader';
import MagicBento from './MagicBento';
import AnimatedInfoList from './AnimatedInfoList';

// Estilos
const listStyle = { margin: 0, paddingLeft: '20px', fontSize: '12px', textAlign: 'left', width: '100%' };
const listItemStyle = { marginBottom: '15px' };
const strongStyle = { color: 'var(--purple-primary)', textTransform: 'uppercase', fontSize: '12px', display: 'block', marginBottom: '4px' };
const scrollableTextStyle = { whiteSpace: 'pre-wrap', padding: '5px', fontSize: '13px' };
const textAreaStyle = { flexGrow: 1, width: '100%', backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'white', padding: '10px', fontFamily: 'inherit', fontSize: '14px', resize: 'none' };
const buttonStyle = { padding: '8px 12px', fontSize: '12px', color: 'var(--white)', backgroundColor: 'var(--purple-primary)', border: 'none', borderRadius: '6px', cursor: 'pointer', opacity: 1, transition: 'opacity 0.2s ease' };
const cardLabelStyle = { fontSize: '18px', fontWeight: '500', marginBottom: '1rem', color: 'var(--white)' };
const cardContentStyle = { width: '100%', height: '100%', display: 'flex', flexDirection: 'column' };
const scrollableContentStyle = { overflowY: 'auto', height: '100%' };

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
            // CORREÇÃO APLICADA AQUI: URL ajustada
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

    const handleFinalizeAndSave = async () => {
        if (!finalNotes) {
            alert("Para finalizar, por favor, descreva sua decisão final no campo de prontuário.");
            return;
        }

        if (!window.confirm("Tem certeza que deseja finalizar e salvar a consulta?")) {
            return;
        }

        console.log("Finalizando e salvando a consulta...");
        setIsLoading(true);

        try {
            const payload = {
                consulta_atual: consulta,
                decisao: {
                    decisao: finalNotes,
                    resumo: "" 
                },
                formato_resumo: "SOAP"
            };

            const response = await fetch(`${API_BASE_URL}/consulta/finalizar/${userId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Falha ao finalizar no servidor.");
            }

            const result = await response.json();
            console.log("Consulta finalizada:", result);
            alert("Consulta salva com sucesso!");

            // MODIFICAÇÃO APLICADA AQUI
            // Passamos a reflexão gerada (result.reflexao) para a função onFinish.
            onFinish(result.reflexao); 

        } catch (error) {
            console.error("Erro ao finalizar a consulta:", error);
            alert(`Ocorreu um erro ao salvar: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    const cardContents = {
        Insights: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Gravador e Transcrição</div>
                {!transcriptionComplete ? (
                    <div style={{flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                        {isLoading ? <HeartbeatLoader /> : <StarButton onClick={handleRecordClick}>{isRecording ? "Parar Gravação" : "Iniciar Gravação"}</StarButton>}
                    </div>
                ) : (
                    <div style={scrollableContentStyle}><p style={scrollableTextStyle}>{transcribedText}</p></div>
                )}
            </div>
        ),
        Overview: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Queixa Principal</div>
                <div style={scrollableContentStyle}><p style={scrollableTextStyle}>{structuredNote.queixa_principal || '...'}</p></div>
            </div>
        ),
        Efficiency: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Análise Clínica</div>
                <div style={scrollableContentStyle}>
                    <strong style={strongStyle}>História da Doença Atual:</strong>
                    <p style={{fontSize: '13px', marginBottom: '1rem'}}>{structuredNote.historia_doenca_atual || '...'}</p>
                    <strong style={strongStyle}>Antecedentes:</strong>
                    <p style={{fontSize: '13px', marginBottom: '1rem'}}>{structuredNote.antecedentes_pessoais_familiares || '...'}</p>
                    <strong style={strongStyle}>Hipóteses Diagnósticas:</strong>
                    <ul style={listStyle}>{(structuredNote.hipoteses_diagnosticas || []).map((h, i) => <li key={i}>{h}</li>)}</ul>
                </div>
            </div>
        ),
        Connectivity: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Exames Sugeridos</div>
                <div style={scrollableContentStyle}>
                    <ul style={listStyle}>
                        {(advancedAnalysis.exames_complementares_sugeridos || []).map((ex, i) => (<li key={i} style={listItemStyle}>{ex.exame}: {ex.justificativa}</li>))}
                    </ul>
                </div>
            </div>
        ),
        Protection: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Tratamentos Sugeridos</div>
                <div style={scrollableContentStyle}>
                    <ul style={listStyle}>
                        {(advancedAnalysis.sugestoes_de_tratamento || []).map((t, i) => (<li key={i} style={listItemStyle}>{t.medicamento_sugerido} ({t.posologia_recomendada}): {t.justificativa_clinica}</li>))}
                    </ul>
                </div>
            </div>
        ),
        Collaboration: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Ações e Prontuário</div>
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '10px' }}>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('receita')}>Gerar Receita</button>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('atestado')}>Gerar Atestado</button>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('pedido_exame')}>Pedir Exames</button>
                </div>
                <textarea style={textAreaStyle} placeholder="Decisão final para o prontuário..." value={finalNotes} onChange={(e) => setFinalNotes(e.target.value)}></textarea>
            </div>
        ),
    };


    return (
        <div style={{backgroundColor: 'var(--background-dark)', color: 'var(--white)'}}>
            <MagicBento cardContents={cardContents} />
            <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                {/* CORREÇÃO APLICADA AQUI: o OnClick foi atualizado */}
                <StarButton onClick={handleFinalizeAndSave}>
                  Finalizar Sessão e Salvar
                </StarButton>
            </div>
        </div>
    );
};

export default ConsultationScreen;