// ConsultationScreen.jsx
import React, { useState, useRef, useEffect } from 'react';
import StarButton from './StarButton';
import HeartbeatLoader from './HeartbeatLoader';
import MagicBento from './MagicBento';
import AnimatedInfoList from './AnimatedInfoList';

// ... (Todas as constantes de estilo permanecem as mesmas) ...
const listStyle = { margin: 0, paddingLeft: '20px', fontSize: '12px', textAlign: 'left', width: '100%' };
const listItemStyle = { marginBottom: '15px' };
const strongStyle = { color: 'var(--purple-primary)', textTransform: 'uppercase', fontSize: '12px', display: 'block', marginBottom: '4px' };
const scrollableTextStyle = { whiteSpace: 'pre-wrap', padding: '5px', fontSize: '13px' };
const textAreaStyle = { flexGrow: 1, width: '100%', backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'white', padding: '10px', fontFamily: 'inherit', fontSize: '14px', resize: 'none' };
const buttonStyle = { padding: '8px 12px', fontSize: '12px', color: 'var(--white)', backgroundColor: 'var(--purple-primary)', border: 'none', borderRadius: '6px', cursor: 'pointer', opacity: 1, transition: 'opacity 0.2s ease' };
const cardLabelStyle = { fontSize: '18px', fontWeight: '500', marginBottom: '1rem', color: 'var(--white)' };
const cardContentStyle = { width: '100%', height: '100%', display: 'flex', flexDirection: 'column' };
const scrollableContentStyle = { overflowY: 'auto', height: '100%' };

const API_BASE_URL = "[https://shaulamed-api-1x9x.onrender.com](https://shaulamed-api-1x9x.onrender.com)";

const ConsultationScreen = ({ userId, onFinish }) => {
    // ... (Os estados de [consulta] até [transcriptionComplete] permanecem os mesmos) ...
    const [consulta, setConsulta] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [transcribedText, setTranscribedText] = useState('');
    const [finalNotes, setFinalNotes] = useState('');
    const [transcriptionComplete, setTranscriptionComplete] = useState(false);
    
    // Novo estado para o botão de gerar resumo
    const [isGeneratingSoap, setIsGeneratingSoap] = useState(false);

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    // Extração de dados atualizada
    const structuredNote = consulta?.sugestao_ia?.nota_clinica_estruturada || {};
    const advancedAnalysis = consulta?.sugestao_ia?.analise_clinica_avancada || {};
    const anamneseData = structuredNote.anamnese || {};

    useEffect(() => {
        // ... (A função startNewConsultation permanece a mesma) ...
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
        // ... (A função handleRecordClick permanece a mesma) ...
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
        // ... (A função handleGenerateDocument permanece a mesma) ...
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

    const handleFinalizeAndSave = async (insight) => {
        // ... (A função handleFinalizeAndSave agora aceita o 'insight' e o passa para onFinish) ...
        if (!finalNotes) {
            alert("Para finalizar, por favor, descreva sua decisão final no campo de prontuário.");
            return;
        }
        if (!window.confirm("Tem certeza que deseja finalizar e salvar a consulta?")) return;
        
        setIsLoading(true);
        try {
            const payload = {
                consulta_atual: consulta,
                decisao: { decisao: finalNotes, resumo: "" },
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
            alert("Consulta salva com sucesso!");
            onFinish(result.reflexao); // Passa a reflexão para a função onFinish
        } catch (error) {
            console.error("Erro ao finalizar a consulta:", error);
            alert(`Ocorreu um erro ao salvar: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };
    
    // ===== NOVA FUNÇÃO ADICIONADA AQUI =====
    const handleGenerateSoap = async () => {
        if (!consulta || !consulta.sugestao_ia) {
            alert("Aguarde a análise da IA estar completa.");
            return;
        }
        setIsGeneratingSoap(true);
        try {
            const payload = {
                dados_consulta: consulta, // Envia a consulta inteira
                formato_resumo: "SOAP"
            };
            const response = await fetch(`${API_BASE_URL}/consulta/gerar_resumo/${userId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error('Falha ao gerar o resumo SOAP.');
            const data = await response.json();
            setFinalNotes(prevNotes => data.resumo_gerado + "\n\n" + prevNotes); // Adiciona no início
        } catch (error) {
            console.error("Erro ao gerar SOAP:", error);
            alert(`Ocorreu um erro: ${error.message}`);
        } finally {
            setIsGeneratingSoap(false);
        }
    };
    // ==========================================


    // ===== MUDANÇA PRINCIPAL AQUI =====
    // O objeto cardContents foi totalmente atualizado para o novo layout
    // e para exibir os dados de forma mais direta.
    
    // Transforma os dados da anamnese para o AnimatedInfoList
    const anamneseList = [
        { label: "Sintoma Principal", value: anamneseData.sintoma_principal },
        { label: "Início e Duração", value: anamneseData.inicio_e_duracao },
        { label: "Sintomas Associados", value: anamneseData.sintomas_associados },
        { label: "Fatores Melhora/Piora", value: anamneseData.fatores_melhora_piora },
        { label: "Antecedentes", value: structuredNote.antecedentes_pessoais_familiares },
        { label: "Exame Físico", value: structuredNote.exame_fisico_verbalizado },
    ].filter(item => item.value); // Filtra itens sem valor

    // Transforma os dados de Exames para incluir a justificativa
    const examesList = (advancedAnalysis.exames_complementares_sugeridos || []).flatMap((ex, i) => [
        { label: `Exame ${i+1}`, value: ex.exame },
        { label: "Justificativa", value: ex.justificativa }
    ]);
    
    // Transforma os dados de Tratamentos para incluir a justificativa
    const tratamentosList = (advancedAnalysis.sugestoes_de_tratamento || []).flatMap((t, i) => [
        { label: `Sugestão ${i+1}`, value: `${t.medicamento_sugerido} (${t.posologia_recomendada})` },
        { label: "Justificativa", value: t.justificativa_clinica }
    ]);


    const cardContents = {
        Gravador: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Gravador e Transcrição</div>
                {!transcriptionComplete ? (
                    <div style={{flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                        {isLoading ? <HeartbeatLoader /> : <StarButton onClick={handleRecordClick}>{isRecording ? "Parar Gravação" : "Analisar"}</StarButton>}
                    </div>
                ) : (
                    <div style={scrollableContentStyle}><p style={scrollableTextStyle}>{transcribedText}</p></div>
                )}
            </div>
        ),
        QueixaPrincipal: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Queixa Principal</div>
                <div style={scrollableContentStyle}><p style={scrollableTextStyle}>{structuredNote.queixa_principal || '...'}</p></div>
            </div>
        ),
        Anamnese: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Resumo da Anamnese</div>
                <div style={scrollableContentStyle}>
                    <AnimatedInfoList items={anamneseList} />
                </div>
            </div>
        ),
        Hipoteses: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Hipóteses Diagnósticas</div>
                <div style={scrollableContentStyle}>
                    <ul style={listStyle}>
                        {(structuredNote.hipoteses_diagnosticas || []).map((h, i) => (
                            <li key={i} style={{...listItemStyle, fontSize: '14px', listStyleType: 'decimal'}}>
                                {h}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        ),
        ExamesSugeridos: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Exames Sugeridos</div>
                <div style={scrollableContentStyle}>
                    <AnimatedInfoList items={examesList} />
                </div>
            </div>
        ),
        TratamentosSugeridos: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Tratamentos Sugeridos</div>
                <div style={scrollableContentStyle}>
                    <AnimatedInfoList items={tratamentosList} />
                </div>
            </div>
        ),
        Acoes: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Ações e Prontuário</div>
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '10px' }}>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('receita')}>Gerar Receita</button>
                    <button style={buttonStyle} onClick={() => handleGenerateDocument('atestado')}>Gerar Atestado</button>
                    <button 
                        style={{...buttonStyle, backgroundColor: isGeneratingSoap ? '#555' : 'var(--purple-secondary)'}} 
                        onClick={handleGenerateSoap}
                        disabled={isGeneratingSoap}
                    >
                        {isGeneratingSoap ? 'A gerar...' : 'Gerar Resumo (SOAP)'}
                    </button>
                </div>
                <textarea style={textAreaStyle} placeholder="Decisão final e notas para o prontuário..." value={finalNotes} onChange={(e) => setFinalNotes(e.target.value)}></textarea>
            </div>
        ),
    };
    // ==========================================


    return (
        <div style={{backgroundColor: 'var(--background-dark)', color: 'var(--white)'}}>
            <MagicBento cardContents={cardContents} />
            <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                <StarButton onClick={handleFinalizeAndSave} disabled={isLoading}>
                  {isLoading ? 'A Salvar...' : 'Finalizar Sessão e Salvar'}
                </StarButton>
            </div>
        </div>
    );
};

export default ConsultationScreen;