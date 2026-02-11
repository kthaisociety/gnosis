import { useCallback, useState } from "react";
import { Upload, FileText, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileUploadZoneProps {
  file: File | null;
  onFileSelect: (file: File | null) => void;
}

const FileUploadZone = ({ file, onFileSelect }: FileUploadZoneProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        const droppedFile = files[0];
        const allowed = [
          "application/pdf",
          "image/png",
          "image/jpeg",
          "image/webp",
          "image/tiff",
          "image/bmp",
        ];
        if (allowed.includes(droppedFile.type)) {
          onFileSelect(droppedFile);
        }
      }
    },
    [onFileSelect],
  );

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const removeFile = () => {
    onFileSelect(null);
  };

  if (file) {
    return (
      <div className="border border-border rounded-lg p-4 bg-secondary/30">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
            <FileText className="w-5 h-5 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{file.name}</p>
            <p className="text-xs text-muted-foreground">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
          <button
            onClick={removeFile}
            className="p-1.5 rounded-md hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <label
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={cn(
        "flex flex-col items-center justify-center gap-3 p-8 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-200",
        isDragging
          ? "border-primary bg-primary/5"
          : "border-border hover:border-muted-foreground/50 hover:bg-secondary/30",
      )}
    >
      <div
        className={cn(
          "p-3 rounded-full transition-colors",
          isDragging ? "bg-primary/20" : "bg-secondary",
        )}
      >
        <Upload
          className={cn(
            "w-6 h-6 transition-colors",
            isDragging ? "text-primary" : "text-muted-foreground",
          )}
        />
      </div>
      <div className="text-center">
        <p className="text-sm font-medium">
          {isDragging ? "Drop your file here" : "Drag & drop an image or PDF"}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          PNG, JPEG, WebP, TIFF, or PDF
        </p>
      </div>
      <input
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.webp,.tiff,.tif,.bmp,application/pdf,image/png,image/jpeg,image/webp,image/tiff,image/bmp"
        onChange={handleFileInput}
        className="hidden"
      />
    </label>
  );
};

export default FileUploadZone;
