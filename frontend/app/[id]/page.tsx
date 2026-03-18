import { redirect } from "next/navigation";

export default function LegacyIncidentRoute({ params }: { params: { id: string } }) {
  redirect(`/incidents/${params.id}`);
}

