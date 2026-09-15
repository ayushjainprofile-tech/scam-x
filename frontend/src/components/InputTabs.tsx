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
    label: 'Urgent Electricity Bill Fraud',
    dotColor: 'dot-warning',
    type: 'text' as InputType,
    content: 'URGENT NOTICE: Dear Customer, your electricity power connection will be disconnected tonight at 9:30 PM because your previous month bill was not updated. Please contact Power Officer Mr. Sharma immediately at 9876543210 to update your payment via APK app.',
    context: 'Received via SMS from unknown number'
  },
  {
    label: 'Fake Bank Account Freeze',
    dotColor: 'dot-danger',
    type: 'text' as InputType,
    content: 'ALERT: Your SBI YONO Account has been blocked today due to pending KYC verification. Click here immediately to unblock your account before 2 hours: http://sbi-kyc-update-login.top/verify. Do not share OTP.',
    context: 'WhatsApp message from unregistered business account'
  },
  {
    label: 'Telegram Job / Prepaid Scam',
    dotColor: 'dot-purple',
    type: 'text' as InputType,
    content: 'Earn ₹5000 to ₹15000 daily working from home! Simple YouTube video liking job. Daily payout guaranteed. Deposit ₹1000 security task to unlock VIP Level 1 high yield earnings.',
    context: 'Telegram group invite'
  },
  {
    label: 'Suspicious Phishing Link',
    dotColor: 'dot-teal',
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
    <div className="command-input-wrapper">
      {/* Segmented Control Bar */}
      <div className="segmented-control-nav" role="tablist" aria-label="Input format selector">
        <button
          role="tab"
          aria-selected={activeTab === 'text'}
          className={`segmented-tab-btn ${activeTab === 'text' ? 'active' : ''}`}
          onClick={() => { setActiveTab('text'); setSelectedFile(null); }}
        >
          <FileText size={16} strokeWidth={1.5} className="tab-icon" />
          <span>Text Message</span>
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'image'}
          className={`segmented-tab-btn ${activeTab === 'image' ? 'active' : ''}`}
          onClick={() => { setActiveTab('image'); setSelectedFile(null); }}
        >
          <ImageIcon size={16} strokeWidth={1.5} className="tab-icon" />
          <span>Screenshot / OCR</span>
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'audio'}
          className={`segmented-tab-btn ${activeTab === 'audio' ? 'active' : ''}`}
          onClick={() => { setActiveTab('audio'); setSelectedFile(null); }}
        >
          <Mic size={16} strokeWidth={1.5} className="tab-icon" />
          <span>Voice Call / Audio</span>
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'url'}
          className={`segmented-tab-btn ${activeTab === 'url' ? 'active' : ''}`}
          onClick={() => { setActiveTab('url'); setSelectedFile(null); }}
        >
          <LinkIcon size={16} strokeWidth={1.5} className="tab-icon" />
          <span>URL Analyzer</span>
        </button>
      </div>

      {/* Demo Presets Row */}
      <div className="presets-command-bar">
        <div className="presets-label">
          <Sparkles size={13} strokeWidth={1.5} className="sparkle-icon" />
          <span>Quick Test Presets:</span>
        </div>
        <div className="preset-chips-row">
          {SAMPLE_PRESETS.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-chip-btn"
              onClick={() => handlePresetSelect(preset)}
            >
              <span className={`preset-dot ${preset.dotColor}`}></span>
              <span className="preset-chip-text">{preset.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Elevated Input Card */}
      <div className="elevated-input-card">
        <form onSubmit={handleSubmit} className="command-form">
          {activeTab === 'text' && (
            <div className="form-group-container">
              <label htmlFor="text-input" className="command-form-label">
                Paste suspicious message, SMS, WhatsApp text, or email body:
              </label>
              <div className="input-focus-ring-wrapper">
                <textarea
                  id="text-input"
                  className="command-textarea"
                  rows={5}
                  placeholder="e.g. URGENT NOTICE: Dear customer, your electricity power connection will be disconnected tonight at 9:30 PM..."
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  required
                />
              </div>
            </div>
          )}

          {activeTab === 'url' && (
            <div className="form-group-container">
              <label htmlFor="url-input" className="command-form-label">
                Enter suspicious link or website URL:
              </label>
              <div className="input-focus-ring-wrapper">
                <input
                  id="url-input"
                  type="url"
                  className="command-input"
                  placeholder="https://sbi-kyc-verify.top/login"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  required
                />
              </div>
              <p className="field-hint-security">
                <AlertCircle size={14} strokeWidth={1.5} /> Passive static analysis — safe evaluation without triggering client execution.
              </p>
            </div>
          )}

          {(activeTab === 'image' || activeTab === 'audio') && (
            <div className="form-group-container">
              <label className="command-form-label">
                {activeTab === 'image' ? 'Upload Screenshot / Image (PNG, JPG, WEBP):' : 'Upload Recorded Call / Voice Note (MP3, WAV, M4A):'}
              </label>
              <div className="file-drop-zone-command">
                <input
                  type="file"
                  id="file-upload"
                  className="file-input-hidden"
                  accept={activeTab === 'image' ? 'image/*' : 'audio/*'}
                  onChange={handleFileChange}
                />
                <label htmlFor="file-upload" className="file-drop-label-command">
                  <Upload size={28} strokeWidth={1.5} className="upload-icon-command" />
                  <span className="file-drop-title">
                    {selectedFile ? selectedFile.name : `Click or drag ${activeTab === 'image' ? 'image screenshot' : 'audio clip'} here`}
                  </span>
                  <span className="file-drop-sub">Maximum file size: 10MB</span>
                </label>
              </div>
              {previewUrl && (
                <div className="image-preview-command">
                  <img src={previewUrl} alt="Upload Preview" className="preview-img-command" />
                </div>
              )}
            </div>
          )}

          <div className="form-group-container context-divider">
            <label htmlFor="context-input" className="command-form-label secondary-label">
              Context / Platform details (optional):
            </label>
            <input
              id="context-input"
              type="text"
              className="command-input secondary-input"
              placeholder="e.g. Received via WhatsApp from unknown mobile number +91-9876543210"
              value={contextInput}
              onChange={(e) => setContextInput(e.target.value)}
            />
          </div>

          <div className="form-actions-command">
            <button
              type="submit"
              className="btn-primary-3d"
              disabled={isLoading || (activeTab === 'text' && !textInput.trim()) || (activeTab === 'url' && !urlInput.trim()) || ((activeTab === 'image' || activeTab === 'audio') && !selectedFile)}
            >
              {isLoading ? (
                <span className="spinner-wrapper">
                  <span className="spinner"></span> Analyzing Threat Indicators...
                </span>
              ) : (
                <>
                  <ShieldAlert size={18} strokeWidth={1.5} className="cta-shield-icon" />
                  <span>Analyze For Scam Indicators</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
