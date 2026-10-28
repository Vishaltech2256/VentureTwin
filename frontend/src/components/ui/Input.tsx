import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  optional?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, optional, className = '', id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="form-group">
        {label && (
          <label htmlFor={inputId} className="form-label">
            <span>{label}</span>
            {optional && <span className="form-label-optional">Optional</span>}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          className={`form-input ${error ? 'error' : ''} ${className}`}
          {...props}
        />
        {error && <p className="form-error">{error}</p>}
        {!error && helperText && <p className="form-help">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
