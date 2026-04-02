import { useState } from "react";
import { Play, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import FileUploadZone from "@/components/FileUploadZone";
import ModelSelector from "@/components/ModelSelector";
import ResultsPanel from "@/components/ResultsPanel";
import { processImage, ApiError, type Runner, type VLMResponse } from "@/lib/api";
import { useHealth } from "@/hooks/useHealth";
import { toast } from "sonner";

const DEFAULT_PROMPT =
  "Extract all data from this image. Return structured JSON with any tables, text, and chart data found.";

const AdminBenchmark = () => {
  const [file, setFile] = useState<File | null>(null);
  const [model, setModel] = useState("nanonets/Nanonets-OCR-s");
  const [runner, setRunner] = useState<Runner>("modal");
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState<VLMResponse | null>(null);
  const [parsedData, setParsedData] = useState<object | null>(null);

  const { isOnline } = useHealth(10_000);

  const handleProcess = async () => {
    if (!file) return;

    setIsProcessing(true);
    setResponse(null);
    setParsedData(null);

    try {
      const result = await processImage({
        file,
        runner,
        config: {
          model_name: model,
          prompt: DEFAULT_PROMPT,
        },
      });

      setResponse(result);

      // Try to parse the text field as JSON; fall back to wrapping it
      if (result.text) {
        try {
          const parsed = JSON.parse(result.text);
          setParsedData(parsed);
        } catch {
          setParsedData({ text: result.text });
        }
      } else {
        setParsedData({});
      }
    } catch (err) {
      if (err instanceof ApiError) {
        toast.error(`Processing failed (${err.status})`, {
          description: err.message,
        });
      } else {
        toast.error("Unexpected error", {
          description: String(err),
        });
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const reset = () => {
    setFile(null);
    setResponse(null);
    setParsedData(null);
  };

  const isOffline = isOnline === false;

  return (
    <div className="flex-1 flex items-center justify-center p-4">
      <div className="w-full max-w-xl animate-scale-in">
        <div className="glass-card rounded-xl p-6">
          <div className="mb-6">
            <h2 className="text-lg font-medium mb-1">Graph Extraction</h2>
            <p className="text-sm text-muted-foreground">
              Upload a scanned PDF or image to extract structured data
            </p>
          </div>

          <div className="space-y-5">
            {/* File Upload */}
            <FileUploadZone file={file} onFileSelect={setFile} />

            {/* Model + Runner Selection */}
            <ModelSelector
              model={model}
              runner={runner}
              onModelChange={setModel}
              onRunnerChange={setRunner}
            />

            {/* Offline warning */}
            {isOffline && (
              <p className="text-xs text-destructive text-center">
                API server is offline — processing unavailable
              </p>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              {parsedData && (
                <Button variant="outline" onClick={reset} className="flex-1">
                  Reset
                </Button>
              )}
              <Button
                onClick={handleProcess}
                disabled={!file || isProcessing || isOffline}
                size="lg"
                className="flex-1"
                variant={file && !isOffline ? "glow" : "default"}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Processing…
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
          {parsedData && response && (
            <>
              {response.inference_time_ms != null && (
                <p className="mt-4 text-xs text-muted-foreground text-center">
                  Inference time: {response.inference_time_ms.toFixed(0)} ms
                </p>
              )}
              <ResultsPanel
                fileName={file?.name ?? "document"}
                model={model}
                data={parsedData}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminBenchmark;
