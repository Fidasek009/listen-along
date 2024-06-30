import { useState, useEffect } from 'react';
import './App.css';
import { getFriends } from './util/APIClient';
import ListItem from './components/ListItem';
import { FriendActivity } from './util/types';

function App() {
	const [friends, setFriends] = useState<Array<FriendActivity>>([]);

    useEffect(() => {
        getFriends().then(friends => setFriends(friends));
    }, []);

    return (
        <div className="App">
			<h1>Listen Along</h1>
			<div className="friend-list-wrapper">
				{[...friends].reverse().map((friend, index) => (
					<ListItem key={index} {...friend} />
				))}
			</div>
            <a href="/api/log" className="log-btn">View Logs</a>
        </div>
    );
}

export default App;
