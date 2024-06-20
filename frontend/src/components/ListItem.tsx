import React, { useState, useEffect } from 'react'
import { FriendActivity } from '../util/types'
import { listenAlong, stopListening } from '../util/APIClient'
import "./ListItem.css"
import { QueueMusic, Album, Person, PlayArrow, Pause } from '@mui/icons-material' // https://mui.com/material-ui/material-icons


const isActive = (timestamp: number): boolean => {
    const diff = Date.now() - timestamp
    // active in the last 10 minutes
    return diff < 600000
}

const openUri = (uri: string) => {
    const [_, type, id] = uri.split(":")
    const url = `https://open.spotify.com/${type}/${id}`
    window.open(url, '_blank')
}

const ListItem: React.FC<FriendActivity> = ({ timestamp, user, track }) => {
    let active = isActive(timestamp)
    let playlist_type = track.context.uri.split(":")[1]
    let playlist_icon = null

    switch (playlist_type) {
        case "playlist":
            playlist_icon = <QueueMusic />
            break
        case "album":
            playlist_icon = <Album />
            break
        case "artist":
            playlist_icon = <Person />
            break
    }

    const [btnColor, setBtnColor] = useState("");
    const [listening, setListening] = useState(false)

    useEffect(() => {
        setBtnColor(active ? listening ? "red" : "green" : "");
    }, [active, listening]);

    const handleClick = async (user_uri: string) => {    
        if(!active) return;

        if (listening) {
            //setBtnColor("green")
            stopListening()
            setListening(false)
            return;
        }

        //setBtnColor("red")
        listenAlong(user_uri)
        setListening(true)
    };

    return (
        <div className="friend-list-item">
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
                    {playlist_icon}
                    <p>{track.context.name}</p>
                </div>
            </div>
            <div className={`listen-btn ${btnColor}`} onClick={() => handleClick(user.uri)}>
                { listening ? <Pause /> : <PlayArrow /> }
            </div>
        </div>
    )
}

export default ListItem
