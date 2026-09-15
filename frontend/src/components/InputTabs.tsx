import React, { useState } from 'react';
import { FileText, Image as ImageIcon, Mic, Link as LinkIcon, Upload, AlertCircle, Sparkles, ShieldAlert } from 'lucide-react';
import type { InputType } from '../types';

interface InputTabsProps {
  onAnalyzeText: (text: string, context: string) => void;
  onAnalyzeImage: (file: File, context: string) => void;
  onAnalyzeAudio: (file: File, context: string) => void;
  onAnalyzeUrl: (url: string, context: string) => void;
  isLoading: boolean;
}

const SAMPLE_PRESETS = [
  {
    label: '⚡ Urgent Electricity Bill Fraud',
    type: 'text' as InputType,
    content: 'URGENT NOTICE: Dear Customer, your electricity power connection will be disconnected tonight at 9:30 PM because your previous month bill was not updated. Please contact Power Officer Mr. Sharma immediately at 9876543210 to update your payment via APK app.',
    context: 'Received via SMS from unknown number'
  },
  {
    label: '🏦 Fake Bank Account Freeze (UPI Scam)',
    type: 'text' as InputType,
    content: 'ALERT: Your SBI YONO Account has been blocked today due to pending KYC verification. Click here immediately to unblock your account before 2 hours: http://sbi-kyc-update-login.top/verify. Do not share OTP.',
    context: 'WhatsApp message from unregistered business account'
  },
  {
    label: '💼 Part-Time Job / Telegram Prepaid Scam',
    type: 'text' as InputType,
    content: 'Earn ₹5000 to ₹15000 daily working from home! Simple YouTube video liking job. Daily payout guaranteed. Deposit ₹1000 security task to unlock VIP Level 1 high yield earnings.',
    context: 'Telegram group invite'
  },
  {
    label: '🔗 Suspicious Phishing URL Check',
    type: 'url' as InputType,
    content: 'https://paytm-kyc-update-portal-fast.tech/refund-login',
    context: 'Link sent in SMS claiming cash back refund'
  }
];

export const InputTabs: React.FC<InputTabsProps> = ({
  onAnalyzeText,
  onAnalyzeImage,
  onAnalyzeAudio,
  onAnalyzeUrl,
  isLoading
}) => {
  const [activeTab, setActiveTab] = useState<InputType>('text');
  const [textInput, setTextInput] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [contextInput, setContextInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setPreviewUrl(reader.result as string);
        };
        reader.readAsDataURL(file);
      } else {
        setPreviewUrl(null);
      }
    }
  };

  const handlePresetSelect = (preset: typeof SAMPLE_PRESETS[0]) => {
    setActiveTab(preset.type);
    if (preset.type === 'text') {
      setTextInput(preset.content);
    } else if (preset.type === 'url') {
      setUrlInput(preset.content);
    }
    setContextInput(preset.context);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;

    if (activeTab === 'text') {
      if (!textInput.trim()) return;
      onAnalyzeText(textInput, contextInput);
    } else if (activeTab === 'url') {
      if (!urlInput.trim()) return;
      onAnalyzeUrl(urlInput, contextInput);
    } else if (activeTab === 'image') {
      if (!selectedFile) return;
      onAnalyzeImage(selectedFile, contextInput);
    } else if (activeTab === 'audio') {
      if (!selectedFile) return;
      onAnalyzeAudio(selectedFile, contextInput);
    }
  };

  return (
    <div className="input-section-card">
      <div className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'text' ? 'active' : ''}`}
          onClick={() => { setActiveTab('text'); setSelectedFile(null); }}
        >
          <FileText size={18} />
          <span>Text Message</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'image' ? 'active' : ''}`}
          onClick={() => { setActiveTab('image'); setSelectedFile(null); }}
        >
          <ImageIcon size={18} />
          <span>Screenshot / OCR</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'audio' ? 'active' : ''}`}
          onClick={() => { setActiveTab('audio'); setSelectedFile(null); }}
        >
          <Mic size={18} />
          <span>Voice Call / Audio</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'url' ? 'active' : ''}`}
          onClick={() => { setActiveTab('url'); setSelectedFile(null); }}
        >
          <LinkIcon size={18} />
          <span>URL Analyzer</span>
        </button>
      </div>

      <div className="presets-container">
        <div className="presets-header">
          <Sparkles size={14} className="sparkle-icon" />
          <span>Quick Demo Presets:</span>
        </div>
        <div className="preset-buttons">
          {SAMPLE_PRESETS.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-pill-btn"
              onClick={() => handlePresetSelect(preset)}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="tab-form">
        {activeTab === 'text' && (
          <div className="form-group">
            <label htmlFor="text-input" className="form-label">
              Paste suspicious message, SMS, WhatsApp text, or email body:
            </label>
            <textarea
              id="text-input"
              className="form-textarea"
              rows={5}
              placeholder="e.g. URGENT: Your bank account will be blocked today due to pending KYC verification..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              required
            />
          </div>
        )}

        {activeTab === 'url' && (
          <div className="form-group">
            <label htmlFor="url-input" className="form-label">
              Enter suspicious link or website URL:
            </label>
            <input
              id="url-input"
              type="url"
              className="form-input"
              placeholder="https://sbi-kyc-verify.top/login"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              required
            />
            <p className="field-hint">
              <AlertCircle size={14} /> SCAMX performs static analysis safely without opening or executing the site.
            </p>
          </div>
        )}

        {(activeTab === 'image' || activeTab === 'audio') && (
          <div className="form-group">
            <label className="form-label">
              {activeTab === 'image' ? 'Upload Screenshot / Image (PNG, JPG, WEBP):' : 'Upload Recorded Call / Voice Note (MP3, WAV, M4A):'}
            </label>
            <div className="file-drop-zone">
              <input
                type="file"
                id="file-upload"
                className="file-input-hidden"
                accept={activeTab === 'image' ? 'image/*' : 'audio/*'}
                onChange={handleFileChange}
              />
              <label htmlFor="file-upload" className="file-drop-label">
                <Upload size={32} className="upload-icon" />
                <span className="file-drop-title">
                  {selectedFile ? selectedFile.name : `Click or drag ${activeTab === 'image' ? 'image screenshot' : 'audio clip'} here`}
                </span>
                <span className="file-drop-sub">Max size 10MB</span>
              </label>
            </div>
            {previewUrl && (
              <div className="image-preview-wrapper">
                <img src={previewUrl} alt="Upload Preview" className="uploaded-preview-img" />
              </div>
            )}
          </div>
        )}

        <div className="form-group context-group">
          <label htmlFor="context-input" className="form-label secondary-label">
            Context / Platform details (optional):
          </label>
          <input
            id="context-input"
            type="text"
            className="form-input secondary-input"
            placeholder="e.g. Received via WhatsApp from unknown number +91-9876543210"
            value={contextInput}
            onChange={(e) => setContextInput(e.target.value)}
          />
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn-submit-analyze"
            disabled={isLoading || (activeTab === 'text' && !textInput.trim()) || (activeTab === 'url' && !urlInput.trim()) || ((activeTab === 'image' || activeTab === 'audio') && !selectedFile)}
          >
            {isLoading ? (
              <span className="spinner-wrapper">
                <span className="spinner"></span> Analyzing Scam Signals...
              </span>
            ) : (
              <>
                <ShieldAlert size={20} />
                <span>Analyze For Scam Indicators</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
