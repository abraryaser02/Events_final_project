import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './App.css'; // Import the app.css file
import ProfileIcon from './ProfileIcon';
import logo from './logo-1.png';
import './map.css';
import profileimg from './profileimg.png';

const imageUrl = profileimg;

function AboutPage() {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
      fetch('http://localhost:5001/all_users')
          .then(response => response.json())
          .then(data => {
              setUsers(data);
              setIsLoading(false);
          })
          .catch(error => {
              setError(error.message);
              setIsLoading(false);
          });
  }, []);

  return (
      <div className="App">
          <div className="top-bar">
              <h1>Friends</h1>
              <ProfileIcon imageUrl="/path/to/image.jpg" /> {/* Update with actual path */}
          </div>
          <div className="left-bar">
              <img src={logo} alt="Logo" id="logo1" />
              <ul>
                  <li><Link to="/events">Events</Link></li>
                  <li><Link to="/map">Map</Link></li>
                  <li><Link to="/about">Friends</Link></li>
                  <li><Link to="/favorites">Favorites</Link></li>
              </ul>
          </div>
          <div className="content">
              <h2>People's Page</h2>
              <ul className="user-list">
                  {isLoading && <div>Loading...</div>}
                  {error && <div>Error: {error}</div>}
                  {users.map(user => (
                      <li key={user.id_users} className="user-item">
                          ID: {user.id_users}, Email: {user.email}
                      </li>
                  ))}
              </ul>
          </div>
      </div>
  );
}

export default AboutPage;
