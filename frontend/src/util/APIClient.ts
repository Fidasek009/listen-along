/**
 * Custom error class for API errors with status codes.
 */
export class APIError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.name = "APIError";
        this.status = status;
    }
}

/**
 * Helper to handle API responses and throw on errors.
 */
async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        let message = `Request failed with status ${response.status}`;
        try {
            const data = await response.json();
            message = data.detail || data.message || message;
        } catch {
            // Response wasn't JSON
        }
        throw new APIError(message, response.status);
    }
    return response.json();
}

/**
 * Fetch friend activity from Spotify.
 */
export async function getFriends() {
    const response = await fetch("/api/get-activity");
    const data = await handleResponse<{ friends: unknown[] }>(response);
    return data.friends;
}

/**
 * Start listening along to a friend.
 */
export async function listenAlong(userUri: string) {
    const response = await fetch(`/api/listen-along?user_uri=${encodeURIComponent(userUri)}`);
    const data = await handleResponse<{ status: string }>(response);
    return data.status;
}

/**
 * Stop listening along.
 */
export async function stopListening() {
    const response = await fetch("/api/stop-listening");
    const data = await handleResponse<{ status: string }>(response);
    return data.status;
}
