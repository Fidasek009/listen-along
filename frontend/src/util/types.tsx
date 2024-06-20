export type User = {
    uri: string
    name: string
    imageUrl: string
}

export type Track = {
    uri: string
    name: string
    imageUrl: string
    album: {
        uri: string
        name: string
    }
    artist: {
        uri: string
        name: string
    }
    context: {
        uri: string
        name: string
        index: number
    }
}

export type FriendActivity = {
    timestamp: number
    user: User
    track: Track
}
