import { useState } from "react";
import { Play, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/Navbar";
import FileUploadZone from "./FileUploadZone";
import ModelSelector from "./ModelSelector";
import ResultsPanel from "./ResultsPanel";

interface BenchmarkCardProps {
  onLogout: () => void;
}

// Mock extracted data
const mockResults = {
  chart_type: "bar_graph",
  title: "Quarterly Revenue Analysis",
  x_axis: {
    label: "Quarter",
    values: ["Q1", "Q2", "Q3", "Q4"],
  },
  y_axis: {
    label: "Revenue (USD)",
    unit: "millions",
  },
  data_points: [
    { quarter: "Q1", value: 45.2 },
    { quarter: "Q2", value: 52.8 },
    { quarter: "Q3", value: 61.4 },
    { quarter: "Q4", value: 73.9 },
  ],
  confidence: 0.94,
  processing_time_ms: 1243,
};

const BenchmarkCard = ({ onLogout }: BenchmarkCardProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [model, setModel] = useState("gpt-4o-vision");
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<object | null>(null);

  const handleProcess = async () => {
    if (!file) return;

    setIsProcessing(true);
    setResults(null);

    // Simulate processing
    await new Promise((resolve) => setTimeout(resolve, 2000));

    setResults(mockResults);
    setIsProcessing(false);
  };

  const reset = () => {
    setFile(null);
    setResults(null);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar onLogout={onLogout} />

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-xl animate-scale-in">
          <div className="glass-card rounded-xl p-6">
            <div className="mb-6">
              <h2 className="text-lg font-medium mb-1">Graph Extraction</h2>
              <p className="text-sm text-muted-foreground">
                Upload a scanned PDF containing graphs to extract data
              </p>
            </div>

            <div className="space-y-5">
              {/* File Upload */}
              <FileUploadZone file={file} onFileSelect={setFile} />

              {/* Model Selection */}
              <ModelSelector value={model} onChange={setModel} />

              {/* Action Buttons */}
              <div className="flex gap-3">
                {results && (
                  <Button variant="outline" onClick={reset} className="flex-1">
                    Reset
                  </Button>
                )}
                <Button
                  onClick={handleProcess}
                  disabled={!file || isProcessing}
                  size="lg"
                  className="flex-1"
                  variant={file ? "glow" : "default"}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Processing...
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
                fileName={file?.name || "document.pdf"}
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
