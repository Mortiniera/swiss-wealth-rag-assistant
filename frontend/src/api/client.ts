export type Source = {
    institution: string;
    document_title: string;
    source_file: string;
    chunk_id: string;
    score: number;
};

export type AskResponse = {
    answer: string;
    sources: Source[];
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

export async function askQuestion(question: string): Promise<AskResponse> {
    const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
    });

    if (!response.ok) {
        const detail = await response.text();
        throw new ApiError(detail || `Request failed (${response.status})`, response.status);
    }

    return response.json() as Promise<AskResponse>;
}