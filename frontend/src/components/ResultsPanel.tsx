import { FileText, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface ResultsPanelProps {
  fileName: string;
  model: string;
  data: object;
}

const ResultsPanel = ({ fileName, model, data }: ResultsPanelProps) => {
  const [copied, setCopied] = useState(false);

  const jsonString = JSON.stringify(data, null, 2);

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-6 border-t border-border pt-6 animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium">Extraction Results</h3>
        <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary border border-primary/20">
          {model}
        </span>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* PDF Preview */}
        <div className="border border-border rounded-lg overflow-hidden bg-secondary/30">
          <div className="px-3 py-2 border-b border-border bg-secondary/50">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <FileText className="w-3.5 h-3.5" />
              <span className="truncate">{fileName}</span>
            </div>
          </div>
          <div className="aspect-[4/3] flex items-center justify-center bg-muted/20">
            <div className="text-center p-6">
              <div className="w-16 h-20 mx-auto mb-3 rounded border border-border bg-card flex items-center justify-center">
                <FileText className="w-8 h-8 text-muted-foreground" />
              </div>
              <p className="text-xs text-muted-foreground">PDF Preview</p>
            </div>
          </div>
        </div>

        {/* JSON Output */}
        <div className="border border-border rounded-lg overflow-hidden bg-secondary/30">
          <div className="px-3 py-2 border-b border-border bg-secondary/50 flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-mono">
              output.json
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={copyToClipboard}
              className="h-7 px-2 text-xs"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  Copy
                </>
              )}
            </Button>
          </div>
          <div className="p-4 max-h-64 overflow-auto">
            <pre className="text-xs font-mono text-muted-foreground whitespace-pre-wrap">
              {jsonString}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPanel;
