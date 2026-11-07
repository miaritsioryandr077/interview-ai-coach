import { useCallback, useEffect, useRef, useState } from "react";

export type RecorderStatus = "idle" | "recording" | "stopped";

/** Durée maximale d'un enregistrement (le backend limite à 10 Mo). */
export const MAX_RECORDING_SECONDS = 180;

/** Type MIME supporté par le navigateur, dans l'ordre de préférence. */
function pickMimeType(): string | undefined {
  if (typeof MediaRecorder === "undefined") return undefined;
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/mp4",
  ];
  return candidates.find((type) => MediaRecorder.isTypeSupported(type));
}

/**
 * Enregistrement micro via MediaRecorder.
 *
 * Le flux est libéré dès l'arrêt (voyant micro éteint) ; le blob reste
 * disponible jusqu'au prochain `start()` ou `reset()`.
 */
export function useAudioRecorder() {
  const [status, setStatus] = useState<RecorderStatus>("idle");
  const [seconds, setSeconds] = useState(0);
  const [blob, setBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);

  const stopTracks = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }, []);

  const clearTimer = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const stop = useCallback(() => {
    clearTimer();
    const recorder = recorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
  }, [clearTimer]);

  const start = useCallback(async () => {
    setError(null);
    setBlob(null);
    setSeconds(0);

    if (
      !navigator.mediaDevices?.getUserMedia ||
      typeof MediaRecorder === "undefined"
    ) {
      setError(
        "L'enregistrement audio n'est pas supporté par ce navigateur. Utilisez la saisie texte.",
      );
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = pickMimeType();
      const recorder = new MediaRecorder(
        stream,
        mimeType ? { mimeType } : undefined,
      );
      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        const type = recorder.mimeType || mimeType || "audio/webm";
        const recorded = new Blob(chunksRef.current, { type });
        chunksRef.current = [];
        setBlob(recorded.size > 0 ? recorded : null);
        setStatus("stopped");
        stopTracks();
      };
      recorder.onerror = () => {
        setError("Une erreur est survenue pendant l'enregistrement.");
        setStatus("idle");
        stopTracks();
      };

      recorder.start();
      setStatus("recording");

      timerRef.current = window.setInterval(() => {
        setSeconds((prev) => {
          const next = prev + 1;
          if (next >= MAX_RECORDING_SECONDS) {
            // Arrêt automatique à la durée maximale.
            window.setTimeout(() => stop(), 0);
          }
          return next;
        });
      }, 1000);
    } catch (err: any) {
      stopTracks();
      setStatus("idle");
      if (err?.name === "NotAllowedError" || err?.name === "SecurityError") {
        setError(
          "Accès au micro refusé. Autorisez le microphone dans votre navigateur ou utilisez la saisie texte.",
        );
      } else if (err?.name === "NotFoundError") {
        setError("Aucun microphone détecté sur cet appareil.");
      } else {
        setError("Impossible de démarrer l'enregistrement audio.");
      }
    }
  }, [stop, stopTracks]);

  const reset = useCallback(() => {
    clearTimer();
    setBlob(null);
    setSeconds(0);
    setStatus("idle");
    setError(null);
  }, [clearTimer]);

  // Nettoyage au démontage : micro coupé, timer arrêté.
  useEffect(() => {
    return () => {
      clearTimer();
      const recorder = recorderRef.current;
      if (recorder && recorder.state !== "inactive") {
        recorder.onstop = null;
        recorder.stop();
      }
      stopTracks();
    };
  }, [clearTimer, stopTracks]);

  return { status, seconds, blob, error, start, stop, reset };
}

/** Formate une durée en secondes au format m:ss. */
export function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}
