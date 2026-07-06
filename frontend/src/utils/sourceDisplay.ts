import type { Source } from "../api/client";

const UNKNOWN_VALUES = new Set(["unknown", ""]);

function inferInstitutionFromFile(sourceFile: string): string | null {
    const base = sourceFile.toLowerCase().replace(/\.txt$/, "");
    if (base.startsWith("ubs")) return "UBS";
    if (base.startsWith("pictet")) return "Pictet";
    if (base.startsWith("lombard_odier") || base.startsWith("lombard odier")) return "Lombard Odier";
    if (base.startsWith("julius_baer")) return "Julius Baer";
    return null;
}

function titleFromFile(sourceFile: string): string {
    const base = sourceFile.split("/").pop()?.replace(/\.txt$/i, "") ?? sourceFile;
    return base
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(" ");
}

export function displayInstitution(source: Source): string {
    if (!UNKNOWN_VALUES.has(source.institution.trim().toLowerCase())) {
        return source.institution;
    }
    return inferInstitutionFromFile(source.source_file) ?? "Unattributed source";
}

export function displayDocumentTitle(source: Source): string {
    if (!UNKNOWN_VALUES.has(source.document_title.trim().toLowerCase())) {
        return source.document_title;
    }
    return titleFromFile(source.source_file);
}

export function displaySourceHeading(source: Source): string {
    return `${displayInstitution(source)} — ${displayDocumentTitle(source)}`;
}

export function relevanceLabel(score: number): "High" | "Medium" | "Low" {
    if (score >= 0.45) return "High";
    if (score >= 0.35) return "Medium";
    return "Low";
}

export function relevanceClassName(score: number): string {
    const label = relevanceLabel(score).toLowerCase();
    return `source-card__relevance source-card__relevance--${label}`;
}
