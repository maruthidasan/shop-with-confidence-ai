import JourneyHeader from "@/components/journey/JourneyHeader";
import AnalysisLoader from "@/components/journey/AnalysisLoader";
export default function AnalysisPage() { return <main className="page-background"><JourneyHeader step={3} /><section className="flex min-h-[calc(100vh-76px)] items-center justify-center px-5 pb-14"><AnalysisLoader /></section></main>; }
