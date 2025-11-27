import { useState, useEffect } from "react";
import "./App.css";
import { getFriends, APIError } from "./util/APIClient";
import ListItem from "./components/ListItem";
import { FriendActivity } from "./util/types";

function App() {
    const [friends, setFriends] = useState<Array<FriendActivity>>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchFriends = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await getFriends();
                setFriends(data as FriendActivity[]);
            } catch (e) {
                if (e instanceof APIError) {
                    setError(`Failed to load friends: ${e.message}`);
                } else {
                    setError("Failed to connect to server");
                }
                console.error(e);
            } finally {
                setLoading(false);
            }
        };

        fetchFriends();
        const interval = setInterval(fetchFriends, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="App">
            <h1>Listen Along</h1>
            {error && <div className="error-banner">{error}</div>}
            {loading && friends.length === 0 && <p>Loading...</p>}
            <div className="friend-list-wrapper">
                {[...friends].reverse().map((friend, index) => (
                    <ListItem key={index} {...friend} />
                ))}
            </div>
            <a href="/api/log" className="log-btn">
                View Logs
            </a>
        </div>
    );
}

export default App;
