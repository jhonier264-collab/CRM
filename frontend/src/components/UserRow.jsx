
import React from 'react';
import { MoreVertical, Star } from 'lucide-react';

const UserRow = ({ user, onDelete }) => {
  return (
    <div className="user-row">
      <div className="user-col checkbox">
        <input type="checkbox" />
      </div>
      <div className="user-col star">
        <Star size={18} className="icon-muted" />
      </div>
      <div className="user-col name">
        <div className="avatar">{user.first_name ? user.first_name[0] : '?'}</div>
        <span>{user.first_name} {user.last_name}</span>
      </div>
      <div className="user-col email">
        {user.email || '-'}
      </div>
      <div className="user-col phone">
        {user.phone || '-'}
      </div>
      <div className="user-col company">
        {user.position && user.company ? `${user.position}, ${user.company}` : (user.company || '-')}
      </div>
      <div className="user-col labels">
         {user.labels && user.labels.slice(0, 2).map((label, i) => (
           <span key={i} className="badge-sm" style={{marginRight: '4px'}}>{label}</span>
         ))}
         {user.labels && user.labels.length > 2 && (
           <span className="badge-sm" style={{background: '#f1f3f4', color: '#5f6368', marginRight: '4px'}}>+{user.labels.length - 2}</span>
         )}
      </div>
      <div className="user-col actions">
        <button className="icon-btn-sm" title="Eliminar" onClick={(e) => {
          e.stopPropagation();
          onDelete(user.id);
        }}>
          <MoreVertical size={16} />
        </button>
      </div>
    </div>
  );
};

export default UserRow;
