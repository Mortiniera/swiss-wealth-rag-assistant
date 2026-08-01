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

/**
 * Label relative to the strongest hit in the same answer.
 * Hybrid RRF scores are ~0.01–0.03, so absolute Chroma thresholds no longer apply.
 */
export function relevanceLabel(
    score: number,
    topScore: number,
): "High" | "Medium" | "Low" {
    if (topScore <= 0 || score <= 0) return "Low";
    const ratio = score / topScore;
    if (ratio >= 0.9) return "High";
    if (ratio >= 0.65) return "Medium";
    return "Low";
}

export function relevanceClassName(score: number, topScore: number): string {
    const label = relevanceLabel(score, topScore).toLowerCase();
    return `source-card__relevance source-card__relevance--${label}`;
}
