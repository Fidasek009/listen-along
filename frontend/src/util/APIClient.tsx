export const getFriends = async () => {
    const response = await fetch("/api/get-activity");
    const data = await response.json();
    console.log(data);
    return data.friends;
}

export const listenAlong = async (user_uri: string) => {
    const response = await fetch(`/api/listen-along?user_uri=${user_uri}`);
    const data = await response.json();
    return data.status;
}

export const stopListening = async () => {
    const response = await fetch(`/api/stop-listening`);
    const data = await response.json();
    return data.status;
}
