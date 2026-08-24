import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bot, LogOut, User as UserIcon, Sparkles } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 glass-card border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2 text-xl font-extrabold tracking-tight text-white group">
          <div className="p-2 bg-gradient-to-tr from-brand-600 to-indigo-500 rounded-xl text-white shadow-lg group-hover:scale-105 transition-transform">
            <Bot className="w-6 h-6" />
          </div>
          <span>
            Interview<span className="text-brand-500">AI</span> Coach
          </span>
        </Link>

        {/* Navigation Actions */}
        <nav className="flex items-center gap-4">
          {user ? (
            <div className="flex items-center gap-4">
              <Link
                to="/dashboard"
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800 transition"
              >
                <Sparkles className="w-4 h-4 text-brand-500" />
                Dashboard
              </Link>

              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-800/80 border border-gray-700 text-sm text-gray-200">
                <UserIcon className="w-4 h-4 text-brand-500" />
                <span className="font-semibold">{user.full_name || user.email}</span>
              </div>

              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-red-400 hover:text-red-300 hover:bg-red-950/40 transition border border-transparent hover:border-red-900/50"
              >
                <LogOut className="w-4 h-4" />
                <span>Déconnexion</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition"
              >
                Connexion
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 rounded-lg shadow-md hover:shadow-brand-500/25 transition-all"
              >
                Inscription
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
};
