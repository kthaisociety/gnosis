import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Bot } from "lucide-react";

interface ModelSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const models = [
  { id: "tesseract", name: "Tesseract OCR", description: "Open source" },
  { id: "gpt-4o-vision", name: "GPT-4o Vision", description: "OpenAI" },
  { id: "claude-3.5-sonnet", name: "Claude 3.5 Sonnet", description: "Anthropic" },
  { id: "gemini-pro-vision", name: "Gemini Pro Vision", description: "Google" },
];

const ModelSelector = ({ value, onChange }: ModelSelectorProps) => {
  return (
    <div className="space-y-2">
      <label className="text-sm text-muted-foreground flex items-center gap-2">
        <Bot className="w-4 h-4" />
        Inference Method
      </label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="w-full bg-background border-border">
          <SelectValue placeholder="Select a model" />
        </SelectTrigger>
        <SelectContent className="bg-popover border-border">
          {models.map((model) => (
            <SelectItem
              key={model.id}
              value={model.id}
              className="focus:bg-accent focus:text-accent-foreground"
            >
              <div className="flex items-center gap-3">
                <span className="font-medium">{model.name}</span>
                <span className="text-xs text-muted-foreground">
                  {model.description}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

export default ModelSelector;
