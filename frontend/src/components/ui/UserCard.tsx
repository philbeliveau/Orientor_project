'use client';
import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import LoadingSpinner from './LoadingSpinner';
import styles from '@/styles/card.module.css';
import { ScoreResponse } from '@/services/hollandTestService';
import AvatarService, { AvatarData } from '@/services/avatarService';

interface UserCardProps {
  name: string;
  role: string;
  skills: string[];
  className?: string;
  style?: React.CSSProperties;
  hollandResults?: ScoreResponse | null;
  loading?: boolean;
  error?: string | null;
}

const riasecColors = {
  R: 'rgba(255, 99, 132, 0.7)',   // Rouge
  I: 'rgba(54, 162, 235, 0.7)',    // Bleu
  A: 'rgba(255, 206, 86, 0.7)',    // Jaune
  S: 'rgba(75, 192, 192, 0.7)',    // Vert
  E: 'rgba(153, 102, 255, 0.7)',   // Violet
  C: 'rgba(255, 159, 64, 0.7)',    // Orange
};

const riasecLabels = {
  R: 'Réaliste',
  I: 'Investigateur',
  A: 'Artistique',
  S: 'Social',
  E: 'Entreprenant',
  C: 'Conventionnel',
};

const UserCard: React.FC<UserCardProps> = ({
  name,
  role,
  skills,
  className,
  style,
  hollandResults,
  loading,
  error
}) => {
  const router = useRouter();
  const [avatarData, setAvatarData] = useState<AvatarData | null>(null);
  const [avatarLoading, setAvatarLoading] = useState(true);

  // Charger l'avatar de l'utilisateur
  useEffect(() => {
    const loadAvatar = async () => {
      try {
        setAvatarLoading(true);
        const data = await AvatarService.getUserAvatar();
        setAvatarData(data);
      } catch (err) {
        console.log('Aucun avatar trouvé pour cet utilisateur');
        setAvatarData(null);
      } finally {
        setAvatarLoading(false);
      }
    };

    loadAvatar();
  }, []);

  const handleProfileClick = () => {
    router.push('/insight');
  };

  const avatarImageUrl = avatarData?.avatar_image_url
    ? AvatarService.getAvatarImageUrl(avatarData.avatar_image_url)
    : null;

  return (
    <div 
      className={`${styles.card} ${className || ''}`} 
      style={{ ...style, cursor: 'pointer' }}
      onClick={handleProfileClick}
    >
      {/* Mail/Settings button */}
      <button className={styles.mail}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Profile picture - Avatar Section (equivalent to profile-pic) */}
      <div className={styles.card__avatar}>
        {avatarLoading ? (
          <div className={styles.avatar__loading}>
            <LoadingSpinner size="md" />
          </div>
        ) : avatarImageUrl ? (
          <Image
            src={avatarImageUrl}
            alt={avatarData?.avatar_name || name}
            width={320}
            height={320}
            className={styles.avatar__image}
          />
        ) : (
          <svg 
            width="100%" 
            height="100%" 
            viewBox="0 0 24 24" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
            className={styles.avatar__placeholder}
          >
            <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2"/>
            <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" stroke="currentColor" strokeWidth="2"/>
          </svg>
        )}
      </div>

      {/* Bottom section with content */}
      <div className={styles.bottom}>
        <div className={styles.content}>
          <span className={styles.card__title}>{avatarData?.avatar_name || name}</span>
          <span className={styles.card__subtitle}>{role}</span>
          
          {/* Avatar Description - will unfold on hover */}
          {avatarData?.avatar_description && (
            <span className={styles.card__description}>{avatarData.avatar_description}</span>
          )}
          
          {/* RIASEC Profile Section - will unfold on hover */}
          {loading ? (
            <div className={styles.card__subtitle} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <LoadingSpinner size="sm" />
              <span>Chargement du profil RIASEC...</span>
            </div>
          ) : error ? (
            <span className={styles.card__subtitle} style={{ color: 'rgba(255, 255, 255, 0.8)' }}>{error}</span>
          ) : hollandResults && hollandResults.top_3_code ? (
            <div className={styles.card__riasec}>
              <div className={styles.card__riasec_codes}>
                {hollandResults.top_3_code.split('').map((letter, index) => (
                  <div
                    key={index}
                    className={styles.card__riasec_code}
                    style={{ backgroundColor: riasecColors[letter as keyof typeof riasecColors] }}
                  >
                    {letter}
                  </div>
                ))}
              </div>
              <span className={styles.card__riasec_label}>
                {riasecLabels[hollandResults.top_3_code[0] as keyof typeof riasecLabels]}
              </span>
            </div>
          ) : (
            <span className={styles.card__subtitle}>Pas de profil RIASEC</span>
          )}
        </div>
        
        {/* Bottom-bottom section with button and social links */}
        <div className={styles.bottom_bottom}>
          <div className={styles.social_links_container}>
            {/* Optional: Add social links here */}
          </div>
          <button 
            className={styles.card__btn} 
            onClick={(e) => {
              e.stopPropagation();
              handleProfileClick();
            }}
          >
            Profile
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserCard;
