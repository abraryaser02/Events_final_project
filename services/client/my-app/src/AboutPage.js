import React from 'react';
import { Link } from 'react-router-dom';
import './App.css'; // Import the app.css file
import ProfileIcon from './ProfileIcon';
import logo from './logo-1.png';
import './map.css';
import profileimg from './profileimg.png';

const imageUrl = profileimg;

function AboutPage() {
  return (
    <div className="App">
      <div className="top-bar">
        <h1>About</h1>
        {/* Profile icon */}
      <ProfileIcon imageUrl={imageUrl} />
      </div>
      <div className="left-bar">
      <img src={logo} alt="Logo" id="logo1" /> {/* Include the logo */}
        <ul>
        <li><Link to="/events">Events</Link></li>
        <li><Link to="/map">Map</Link></li>
        <li><Link to="/about">About</Link></li>
        </ul>
      </div>
      <header className="About-header">
        <h2>AI-Powered Event Planner for 5Cs Students</h2>
        <p>P-5cEvents is a web app designed to organize events and calendars, offering comprehensive event scheduling assistance</p>
      </header>
      <header className="About-team">
        <h2>Meet the dev</h2>
        <p>Abrar Yaser POM '25</p>

      </header>
    </div>
  );
}

export default AboutPage;
