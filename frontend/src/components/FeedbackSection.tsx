import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Check, Sparkles } from 'lucide-react';
import { submitFeedback } from '../api/client';
import type { EducationalTip as EducationalTipType } from '../types';

interface FeedbackSectionProps {
  analysisId: string;
}

export const FeedbackSection: React.FC<FeedbackSectionProps> = ({ analysisId }) => {
  const [submitted, setSubmitted] = useState(false);
  const [isAccurate, setIsAccurate] = useState<boolean | null>(null);
  const [comment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleVote = async (accurate: boolean) => {
    setIsAccurate(accurate);
    setIsSubmitting(true);
    try {
      await submitFeedback({
        analysis_id: analysisId,
        is_accurate: accurate,
        user_comment: comment,
      });
      setSubmitted(true);
    } catch {
      setSubmitted(true); // Graceful UX
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="feedback-submitted-box">
        <Check size={18} className="text-success" />
        <span>Thank you! Your feedback helps train SCAMX risk models.</span>
      </div>
    );
  }

  return (
    <div className="feedback-card">
      <span className="feedback-title">Was this analysis accurate & helpful?</span>
      <div className="feedback-buttons">
        <button
          className={`btn-feedback ${isAccurate === true ? 'active-thumb' : ''}`}
          onClick={() => handleVote(true)}
          disabled={isSubmitting}
        >
          <ThumbsUp size={16} /> Accurate
        </button>
        <button
          className={`btn-feedback ${isAccurate === false ? 'active-thumb' : ''}`}
          onClick={() => handleVote(false)}
          disabled={isSubmitting}
        >
          <ThumbsDown size={16} /> Inaccurate
        </button>
      </div>
    </div>
  );
};

interface EducationalTipCardProps {
  tip: EducationalTipType;
}

export const EducationalTipCard: React.FC<EducationalTipCardProps> = ({ tip }) => {
  return (
    <div className="edu-tip-card">
      <div className="edu-header">
        <Sparkles size={18} className="edu-icon" />
        <span className="edu-category">{tip.category} Tip</span>
      </div>
      <h4 className="edu-title">{tip.title}</h4>
      <p className="edu-content">{tip.content}</p>
    </div>
  );
};
