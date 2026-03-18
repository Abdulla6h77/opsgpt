import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface RemediationListProps {
  text: string;
}

function toBullets(text: string): string[] {
  if (!text.trim()) {
    return ["Manual investigation required."];
  }
  return text
    .split(/\n|\. /)
    .map((step) => step.trim().replace(/\.$/, ""))
    .filter(Boolean);
}

export function RemediationList({ text }: RemediationListProps) {
  const items = toBullets(text);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Remediation Steps</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="list-disc space-y-2 pl-5 text-sm">
          {items.map((step, idx) => (
            <li key={`${step}-${idx}`}>{step}</li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

