import { useState } from "react";
import { Play, Loader2, AlertCircle, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/Navbar";
import FileUploadZone from "./FileUploadZone";
import ModelSelector from "./ModelSelector";
import ResultsPanel from "./ResultsPanel";
import HealthIndicator from "./HealthIndicator";
import { useHealth } from "@/hooks/useHealth";
import {
  processImage,
  ApiError,
  type Runner,
  type VLMResponse,
} from "@/lib/api";

interface BenchmarkCardProps {
  onLogout: () => void;
}

const DEFAULT_PROMPT =
  "Extract all data from this image. Return structured JSON with any tables, text, and chart data found.";

const BenchmarkCard = ({ onLogout }: BenchmarkCardProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [model, setModel] = useState("nanonets/Nanonets-OCR-s");
  const [runner, setRunner] = useState<Runner>("modal");
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<VLMResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const healthState = useHealth();
  const canProcess = file && !isProcessing && healthState.isOnline === true;

  const handleProcess = async () => {
    if (!file) return;

    setIsProcessing(true);
    setResults(null);
    setError(null);

    try {
      const response = await processImage({
        file,
        runner,
        config: {
          model_name: model,
          prompt: DEFAULT_PROMPT,
          use_gpu: runner === "modal",
          attn_implementation: runner === "modal" ? "sdpa" : undefined,
        },
      });
      setResults(response);
    } catch (err) {
      if (err instanceof ApiError) {
        const detail =
          typeof err.message === "string"
            ? err.message
            : JSON.stringify(err.message);
        setError(`Error ${err.status}: ${detail}`);
      } else {
        setError("Failed to connect to the API. Is the gateway running?");
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const reset = () => {
    setFile(null);
    setResults(null);
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar onLogout={onLogout} />

      {/* Health status bar */}
      <div className="max-w-5xl mx-auto w-full px-4 py-2 flex justify-end">
        <HealthIndicator health={healthState} />
      </div>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-xl animate-scale-in">
          <div className="glass-card rounded-xl p-6">
            <div className="mb-6">
              <h2 className="text-lg font-medium mb-1">Graph Extraction</h2>
              <p className="text-sm text-muted-foreground">
                Upload a scanned image or PDF containing graphs to extract data
              </p>
            </div>

            <div className="space-y-5">
              {/* File Upload */}
              <FileUploadZone file={file} onFileSelect={setFile} />

              {/* Model & Runner Selection */}
              <ModelSelector
                model={model}
                runner={runner}
                onModelChange={setModel}
                onRunnerChange={setRunner}
              />

              {/* Error Display */}
              {error && (
                <div className="flex items-start gap-3 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                  <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                  <p>{error}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3">
                {(results || error) && (
                  <Button variant="outline" onClick={reset} className="flex-1">
                    Reset
                  </Button>
                )}
                <Button
                  onClick={handleProcess}
                  disabled={!canProcess}
                  size="lg"
                  className="flex-1"
                  variant={canProcess ? "glow" : "default"}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Processing...
                    </>
                  ) : healthState.isOnline === false ? (
                    <>
                      <WifiOff className="w-4 h-4" />
                      API Offline
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Process
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Results */}
            {results && (
              <ResultsPanel
                fileName={file?.name || "document"}
                model={model}
                data={results}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default BenchmarkCard;
