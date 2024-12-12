import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./VillancicoGenerator.css";

const VillancicoGenerator = () => {
    const [prompt, setPrompt] = useState("");
    const [villancico, setVillancico] = useState(null);
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const titleRef = useRef(null);

    useEffect(() => {
        const title = titleRef.current;
        let animationId;

        const animate = () => {
            const time = Date.now() / 1000;
            const offsetX = Math.sin(time) * 5;
            const offsetY = Math.cos(time) * 3;
            title.style.transform = `translate(${offsetX}px, ${offsetY}px) rotate(${offsetX / 2}deg)`;
            animationId = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            cancelAnimationFrame(animationId);
        };
    }, []);

    const generateVillancico = async () => {
        if (!prompt.trim()) {
            alert("Por favor, introduce un tema para generar el villancico.");
            return;
        }

        stopPlayback();
        setLoading(true);
        setError(null);

        try {
            const response = await axios.post(
                `${process.env.REACT_APP_BACKEND_URL}/generate_villancico`,
                { prompt }
            );
            setVillancico(response.data.letra);
            setImageUrl(null);
            generateImage(response.data.letra);
        } catch (err) {
            console.error("Error al generar el villancico:", err);
            setError("Hubo un error al generar el villancico.");
        } finally {
            setLoading(false);
        }
    };

    const generateImage = async (text = prompt) => {
        setLoading(true);
        setError(null);

        try {
            const response = await axios.post(
                `${process.env.REACT_APP_BACKEND_URL}/generate_image`,
                { prompt: text }
            );
            setImageUrl(response.data.image_url);
        } catch (err) {
            console.error("Error al generar la imagen:", err);
            setError("Hubo un error al generar la imagen.");
        } finally {
            setLoading(false);
        }
    };

    const playVillancico = () => {
        if (!villancico || isPlaying) return;

        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance(villancico);

        utterance.onend = () => {
            setIsPlaying(false);
        };

        setIsPlaying(true);
        synth.speak(utterance);
    };

    const stopPlayback = () => {
        if (isPlaying) {
            window.speechSynthesis.cancel();
            setIsPlaying(false);
        }
    };

    const resetVillancico = () => {
        stopPlayback();
        setVillancico(null);
        setImageUrl(null);
        setPrompt("");
        setError(null);
    };

    const downloadVillancico = () => {
        const element = document.createElement("a");
        const file = new Blob([villancico], {type: 'text/plain'});
        element.href = URL.createObjectURL(file);
        element.download = "villancico.txt";
        document.body.appendChild(element);
        element.click();
    };

    const downloadImage = () => {
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = 'postal_navideña.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="villancico-generator">
            <div className="title-container">
                <div className="title" ref={titleRef}>
                    <h1>Generador de Villancicos</h1>
                </div>
            </div>
            <div className="content">
                <div className="input-section">
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Escribe un tema para tu villancico..."
                        className="prompt-input"
                    />
                    <div className="button-group">
                        <button
                            onClick={generateVillancico}
                            className={`action-button ${loading ? "loading" : ""}`}
                            disabled={loading || !prompt.trim()}
                        >
                            {loading ? "Generando..." : "Generar Villancico"}
                        </button>
                        <button
                            onClick={() => generateImage()}
                            className="action-button"
                            disabled={loading || !prompt.trim()}
                        >
                            Generar Postal Navideña
                        </button>
                        <button
                            onClick={resetVillancico}
                            className="action-button reset-button"
                            disabled={loading || (!villancico && !imageUrl)}
                        >
                            Volver a Generar
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="error-message">
                        <p>{error}</p>
                    </div>
                )}

                <div className="output-container">
                    {villancico && (
                        <div className="output villancico-output">
                            <h2>🎶 Villancico Generado</h2>
                            <p>{villancico}</p>
                            <div className="button-group">
                                <button
                                    onClick={playVillancico}
                                    className="action-button"
                                    disabled={isPlaying}
                                >
                                    {isPlaying ? "Reproduciendo..." : "Reproducir Villancico"}
                                </button>
                                <button
                                    onClick={downloadVillancico}
                                    className="action-button"
                                >
                                    Descargar Villancico
                                </button>
                            </div>
                        </div>
                    )}

                    {imageUrl && (
                        <div className="output image-output">
                            <h2>🌟 Postal Navideña</h2>
                            <img src={imageUrl} alt="Postal Navideña generada" className="generated-image" />
                            <button
                                onClick={downloadImage}
                                className="action-button"
                            >
                                Descargar Imagen
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default VillancicoGenerator;