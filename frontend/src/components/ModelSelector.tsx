import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Bot, Server } from "lucide-react";
import type { Runner } from "@/lib/api";

interface ModelSelectorProps {
  model: string;
  runner: Runner;
  onModelChange: (value: string) => void;
  onRunnerChange: (value: Runner) => void;
}

const models = [
  {
    id: "nanonets/Nanonets-OCR-s",
    name: "Nanonets OCR-s",
    description: "Fast & accurate",
  },
  {
    id: "gemini-2.5-flash",
    name: "Gemini 2.5 Flash",
    description: "Google",
  },
];

const runners: { id: Runner; name: string; description: string }[] = [
  { id: "modal", name: "Modal (Cloud GPU)", description: "Remote GPU" },
  { id: "local", name: "Local (gRPC)", description: "Local server" },
];

const ModelSelector = ({
  model,
  runner,
  onModelChange,
  onRunnerChange,
}: ModelSelectorProps) => {
  return (
    <div className="space-y-4">
      {/* Model Selection */}
      <div className="space-y-2">
        <label className="text-sm text-muted-foreground flex items-center gap-2">
          <Bot className="w-4 h-4" />
          Model
        </label>
        <Select value={model} onValueChange={onModelChange}>
          <SelectTrigger className="w-full bg-background border-border">
            <SelectValue placeholder="Select a model" />
          </SelectTrigger>
          <SelectContent className="bg-popover border-border">
            {models.map((m) => (
              <SelectItem
                key={m.id}
                value={m.id}
                className="focus:bg-accent focus:text-accent-foreground"
              >
                <div className="flex items-center gap-3">
                  <span className="font-medium">{m.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {m.description}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Runner Selection */}
      <div className="space-y-2">
        <label className="text-sm text-muted-foreground flex items-center gap-2">
          <Server className="w-4 h-4" />
          Inference Runner
        </label>
        <Select
          value={runner}
          onValueChange={(v) => onRunnerChange(v as Runner)}
        >
          <SelectTrigger className="w-full bg-background border-border">
            <SelectValue placeholder="Select runner" />
          </SelectTrigger>
          <SelectContent className="bg-popover border-border">
            {runners.map((r) => (
              <SelectItem
                key={r.id}
                value={r.id}
                className="focus:bg-accent focus:text-accent-foreground"
              >
                <div className="flex items-center gap-3">
                  <span className="font-medium">{r.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {r.description}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};

export default ModelSelector;
