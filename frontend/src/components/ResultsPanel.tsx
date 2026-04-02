import { useEffect, useState } from "react";
import { FileText, Copy, Check, File as FileIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ResultsPanelProps {
  fileName: string;
  model: string;
  data: object;
  file: File;
}

const BROWSER_PREVIEW_IMAGES = ["image/png", "image/jpeg", "image/webp"];

function FilePreview({ file }: { file: File }) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);

  useEffect(() => {
    const url = URL.createObjectURL(file);
    setObjectUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  if (!objectUrl) return null;

  if (file.type === "application/pdf") {
    return (
      <iframe
        src={objectUrl}
        className="w-full rounded-b-lg"
        style={{ height: "300px" }}
        title="PDF preview"
      />
    );
  }

  if (BROWSER_PREVIEW_IMAGES.includes(file.type)) {
    return (
      <img
        src={objectUrl}
        alt="Preview"
        className="w-full rounded-b-lg object-contain bg-muted/20"
        style={{ maxHeight: "300px" }}
      />
    );
  }

  // TIFF, BMP — not natively renderable
  return (
    <div className="w-full flex flex-col items-center justify-center gap-2 py-10 bg-muted/20 rounded-b-lg">
      <FileIcon className="w-10 h-10 text-muted-foreground" />
      <p className="text-xs text-muted-foreground">
        Preview not available for {file.type.split("/")[1].toUpperCase()}
      </p>
    </div>
  );
}

const ResultsPanel = ({ fileName, model, data, file }: ResultsPanelProps) => {
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
        {/* File Preview */}
        <div className="border border-border rounded-lg overflow-hidden bg-secondary/30">
          <div className="px-3 py-2 border-b border-border bg-secondary/50">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <FileText className="w-3.5 h-3.5" />
              <span className="truncate">{fileName}</span>
            </div>
          </div>
          <FilePreview file={file} />
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
          <div className="p-4 max-h-[300px] overflow-auto">
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
