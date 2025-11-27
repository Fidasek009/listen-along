import React, { useState, useEffect } from "react";
import { FriendActivity } from "../util/types";
import { listenAlong, stopListening } from "../util/APIClient";
import "./ListItem.css";
import { QueueMusic, Album, Person, PlayArrow, Pause } from "@mui/icons-material";

const isActive = (timestamp: number): boolean => {
    const diff = Date.now() - timestamp;
    return diff < 600000;
};

const getLastActivityString = (timestamp: number): string => {
    const diff = (Date.now() - timestamp) / 1000;
    const seconds = diff % 60;
    const minutes = Math.floor(diff / 60) % 60;
    const hours = Math.floor(diff / 3600) % 24;
    const days = Math.floor(diff / 86400);

    if (days > 0) return `${days}d`;
    if (hours > 0) return `${hours}h`;
    return `${minutes}:${seconds < 10 ? "0" : ""}${Math.floor(seconds)}`;
};

const openUri = (uri: string) => {
    const [, type, id] = uri.split(":");
    const url = `https://open.spotify.com/${type}/${id}`;
    window.open(url, "_blank");
};

const ListItem: React.FC<FriendActivity> = ({ timestamp, user, track }) => {
    const active = isActive(timestamp);
    const playlistType = track.context.uri.split(":")[1];

    const getPlaylistIcon = () => {
        switch (playlistType) {
            case "playlist":
                return <QueueMusic />;
            case "album":
                return <Album />;
            case "artist":
                return <Person />;
            default:
                return null;
        }
    };

    const [btnColor, setBtnColor] = useState("");
    const [listening, setListening] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setBtnColor(active ? (listening ? "red" : "green") : "");
    }, [active, listening]);

    const handleClick = async (userUri: string) => {
        if (!active) return;

        setError(null);
        try {
            if (listening) {
                await stopListening();
            } else {
                await listenAlong(userUri);
            }
            setListening(!listening);
        } catch (e) {
            const message = e instanceof Error ? e.message : "Unknown error";
            setError(message);
            console.error("Listen action failed:", e);
        }
    };

    return (
        <div className="friend-list-item">
            {error && <div className="item-error">{error}</div>}
            <div className="list-user" onClick={() => openUri(user.uri)}>
                <img src={user.imageUrl || "/unknown.png"} alt="user" />
                <p>{user.name}</p>
            </div>
            <div className="list-info">
                <div className="list-track" onClick={() => openUri(track.uri)}>
                    <img src={track.imageUrl} alt="track" />
                    <div>
                        <p className="trackName">{track.name}</p>
                        <p className="artistName">{track.artist.name}</p>
                    </div>
                </div>
                <div className="list-playlist" onClick={() => openUri(track.context.uri)}>
                    {getPlaylistIcon()}
                    <p>{track.context.name}</p>
                </div>
            </div>
            <div className="list-play">
                <div className={`listen-btn ${btnColor}`} onClick={() => handleClick(user.uri)}>
                    {listening ? <Pause /> : <PlayArrow />}
                </div>
                <p>{getLastActivityString(timestamp)}</p>
            </div>
        </div>
    );
};

export default ListItem;
