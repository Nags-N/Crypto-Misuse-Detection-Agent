import React from 'react';
import './PanelLayout.css';

function PanelLayout({ left, center, right }) {
  return (
    <div className="panel-layout">
      <div className="panel left-panel">
        {left}
      </div>
      <div className="panel center-panel">
        {center}
      </div>
      <div className="panel right-panel">
        {right}
      </div>
    </div>
  );
}

export default PanelLayout;
