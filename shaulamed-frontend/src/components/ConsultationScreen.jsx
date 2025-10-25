// ConsultationScreen.jsx
import React, { useState, useRef, useEffect } from 'react';
import StarButton from './StarButton';
import HeartbeatLoader from './HeartbeatLoader';
import MagicBento from './MagicBento';
import AnimatedInfoList from './AnimatedInfoList';

// Estilos (mantidos como constantes para clareza)
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
    const [isGeneratingSoap, setIsGeneratingSoap] = useState(false);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    // Extração segura dos dados da consulta
    const structuredNote = consulta?.sugestao_ia?.nota_clinica_estruturada || {};
    const advancedAnalysis = consulta?.sugestao_ia?.analise_clinica_avancada || {};
    const anamneseData = structuredNote.anamnese || {};

    // Efeito para iniciar a consulta quando o userId estiver disponível
    useEffect(() => {
        const startNewConsultation = async () => {
            // VERIFICA SE O USERID EXISTE ANTES DE CHAMAR A API
            if (!userId) {
                console.log("ConsultationScreen: Aguardando userId...");
                return; // Sai da função se não houver userId
            }

            try {
                console.log(`ConsultationScreen: Iniciando consulta para o usuário: ${userId}`);
                const response = await fetch(`${API_BASE_URL}/consulta/iniciar/${userId}`, { method: 'POST' });
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Falha ao iniciar consulta na API. Status: ${response.status}. Detalhes: ${errorText}`);
                }
                const data = await response.json();
                setConsulta(data);
                console.log("ConsultationScreen: Consulta iniciada com sucesso:", data);
            } catch (error) {
                console.error("ConsultationScreen: Erro ao iniciar nova consulta:", error);
                alert(`Não foi possível iniciar a consulta: ${error.message}. Verifique sua conexão ou tente logar novamente.`);
                // Se falhar, retorna para a Home (ou Login)
                onFinish(null);
            }
        };
        startNewConsultation();
    }, [userId, onFinish]); // Dependências do efeito

    // Função para gravar e processar o áudio
    const handleRecordClick = async () => {
        if (isRecording) {
            if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
                mediaRecorderRef.current.stop(); // Para a gravação
            }
            setIsRecording(false);
            // O processamento acontece no onstop
        } else {
            // Iniciar Gravação
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' }); // Especificar mimeType pode ajudar
                    audioChunksRef.current = [];

                    mediaRecorderRef.current.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            audioChunksRef.current.push(event.data);
                        }
                    };

                    mediaRecorderRef.current.onstop = async () => {
                        setIsLoading(true); // Mostra o loader
                        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                        const formData = new FormData();
                        formData.append("ficheiro_audio", audioBlob, "consulta.webm");

                        try {
                            // 1. Transcrever
                            const transResponse = await fetch(`${API_BASE_URL}/audio/transcrever`, { method: 'POST', body: formData });
                            if (!transResponse.ok) {
                                const errorText = await transResponse.text();
                                throw new Error(`Falha na transcrição. Status: ${transResponse.status}. Detalhes: ${errorText}`);
                            }
                            const transData = await transResponse.json();
                            setTranscribedText(transData.texto_transcrito);

                            // 2. Processar (usando o userId real)
                            const payload = { consulta_atual: consulta, fala: { texto: transData.texto_transcrito } };
                            const processResponse = await fetch(`${API_BASE_URL}/consulta/processar/${userId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                            if (!processResponse.ok) {
                                const errorText = await processResponse.text();
                                throw new Error(`Falha ao processar a consulta. Status: ${processResponse.status}. Detalhes: ${errorText}`);
                            }
                            const processData = await processResponse.json();
                            setConsulta(processData); // Atualiza o estado da consulta com a análise da IA
                            setTranscriptionComplete(true); // Marca que a análise foi feita

                        } catch (error) {
                            console.error("ConsultationScreen: Erro no processo de gravação-análise:", error);
                            alert(`Ocorreu um erro durante a análise: ${error.message}`);
                        } finally {
                            setIsLoading(false); // Esconde o loader
                        }
                    };

                    mediaRecorderRef.current.start();
                    setIsRecording(true);
                } catch (err) {
                    console.error("ConsultationScreen: Erro ao obter acesso ao microfone:", err);
                    alert("Não foi possível aceder ao microfone. Verifique as permissões do navegador.");
                }
            } else {
                alert("Seu navegador não suporta gravação de áudio.");
            }
        }
    };

    // Função para gerar documentos
    const handleGenerateDocument = async (docType) => {
        if (!consulta || !consulta.sugestao_ia?.nota_clinica_estruturada) {
            alert("Aguarde a análise da IA estar completa para gerar documentos.");
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
            setFinalNotes(prevNotes => prevNotes + documentText); // Adiciona ao final das notas
        } catch (error) {
            console.error(`ConsultationScreen: Erro ao gerar ${docType}:`, error);
            alert(`Ocorreu um erro ao gerar o documento: ${error.message}`);
        }
    };

    // Função para finalizar e salvar a consulta
    const handleFinalizeAndSave = async () => {
        if (!finalNotes) {
            alert("Para finalizar, por favor, descreva sua decisão final no campo de prontuário.");
            return;
        }
        if (!window.confirm("Tem certeza que deseja finalizar e salvar a consulta?")) return;

        setIsLoading(true); // Mostra loader no botão de finalizar
        try {
            const payload = {
                consulta_atual: consulta,
                decisao: { decisao: finalNotes, resumo: "" }, // 'resumo' não é mais necessário aqui
                formato_resumo: "SOAP" // O backend usa isso para a lógica interna
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
            onFinish(result.reflexao); // Passa a reflexão para o App.jsx
        } catch (error) {
            console.error("ConsultationScreen: Erro ao finalizar a consulta:", error);
            alert(`Ocorreu um erro ao salvar: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    // Função para gerar o resumo SOAP
    const handleGenerateSoap = async () => {
        if (!consulta || !consulta.sugestao_ia) {
            alert("Aguarde a análise da IA estar completa.");
            return;
        }
        setIsGeneratingSoap(true);
        try {
            const payload = {
                // O endpoint agora espera 'dados_consulta' que é o objeto 'consulta' inteiro
                dados_consulta: consulta,
                formato_resumo: "SOAP"
            };
            const response = await fetch(`${API_BASE_URL}/consulta/gerar_resumo/${userId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                 const errorText = await response.text();
                 throw new Error(`Falha ao gerar o resumo SOAP. Status: ${response.status}. Detalhes: ${errorText}`);
            }
            const data = await response.json();
            // Adiciona o resumo gerado ao início do campo de notas
            setFinalNotes(prevNotes => data.resumo_gerado + (prevNotes ? "\n\n" + prevNotes : ""));
        } catch (error) {
            console.error("ConsultationScreen: Erro ao gerar SOAP:", error);
            alert(`Ocorreu um erro ao gerar o resumo: ${error.message}`);
        } finally {
            setIsGeneratingSoap(false);
        }
    };

    // Mapeamento dos dados para os cards (já corrigido na resposta anterior)
    const anamneseList = [
        { label: "Sintoma Principal", value: anamneseData.sintoma_principal },
        { label: "Início e Duração", value: anamneseData.inicio_e_duracao },
        { label: "Sintomas Associados", value: anamneseData.sintomas_associados },
        { label: "Fatores Melhora/Piora", value: anamneseData.fatores_melhora_piora },
        { label: "Antecedentes", value: structuredNote.antecedentes_pessoais_familiares },
        { label: "Exame Físico", value: structuredNote.exame_fisico_verbalizado },
    ].filter(item => item.value);

    const examesList = (advancedAnalysis.exames_complementares_sugeridos || []).flatMap((ex, i) => [
        { label: `Exame ${i+1}`, value: ex.exame },
        { label: "Justificativa", value: ex.justificativa }
    ]);

    const tratamentosList = (advancedAnalysis.sugestoes_de_tratamento || []).flatMap((t, i) => [
        { label: `Sugestão ${i+1}`, value: `${t.medicamento_sugerido} (${t.posologia_recomendada})` },
        { label: "Justificativa", value: t.justificativa_clinica }
    ]);

    // Definição do conteúdo de cada card
    const cardContents = {
        Gravador: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Gravador e Transcrição</div>
                {!transcriptionComplete ? (
                    <div style={{flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                        {/* Desabilita o botão se a consulta não foi iniciada */}
                        {isLoading ? <HeartbeatLoader /> : <StarButton onClick={handleRecordClick} disabled={!consulta}>{isRecording ? "Analisar" : "Iniciar Gravação"}</StarButton>}
                    </div>
                ) : (
                    <div style={scrollableContentStyle}><p style={scrollableTextStyle}>{transcribedText}</p></div>
                )}
            </div>
        ),
        QueixaPrincipal: (
            <div style={cardContentStyle}>
                <div style={cardLabelStyle}>Queixa Principal</div>
                <div style={scrollableContentStyle}><p style={scrollableTextStyle}>{structuredNote.queixa_principal || 'Aguardando análise...'}</p></div>
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
                        {(!structuredNote.hipoteses_diagnosticas || structuredNote.hipoteses_diagnosticas.length === 0) && <p>...</p>}
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
                        disabled={isGeneratingSoap || !consulta} // Desabilita se estiver gerando ou se não houver consulta
                    >
                        {isGeneratingSoap ? 'A gerar...' : 'Gerar Resumo (SOAP)'}
                    </button>
                </div>
                <textarea style={textAreaStyle} placeholder="Decisão final e notas para o prontuário..." value={finalNotes} onChange={(e) => setFinalNotes(e.target.value)}></textarea>
            </div>
        ),
    };

    // Renderização principal do componente
    return (
        <div style={{backgroundColor: 'var(--background-dark)', color: 'var(--white)'}}>
            <MagicBento cardContents={cardContents} />
            <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                <StarButton onClick={handleFinalizeAndSave} disabled={isLoading || !consulta}>
                  {isLoading ? 'A Salvar...' : 'Finalizar Sessão e Salvar'}
                </StarButton>
            </div>
        </div>
    );
};

export default ConsultationScreen;