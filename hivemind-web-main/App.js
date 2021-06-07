import Dashboard from './views/Dashboard';
import {BrowserRouter as Router, Route} from "react-router-dom";
import React from 'react';

function App() {
    return (
        <div>
            <Router>
                <div>
                    <Route exact path='/'>
                        <Dashboard/>
                    </Route>
                </div>
            </Router>
        </div>
    );
}

export default App;