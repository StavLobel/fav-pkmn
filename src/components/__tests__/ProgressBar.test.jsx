import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProgressBar from '../ProgressBar';

describe('ProgressBar', () => {
  it('CT-PB-01: renders at 0%', () => {
    render(<ProgressBar current={0} total={100} />);

    const fill = screen.getByTestId('progress-bar-fill');
    expect(fill).toHaveStyle({ width: '0%' });
  });

  it('CT-PB-02: renders at 50%', () => {
    render(<ProgressBar current={50} total={100} />);

    const fill = screen.getByTestId('progress-bar-fill');
    expect(fill).toHaveStyle({ width: '50%' });
  });

  it('CT-PB-03: renders at 100%', () => {
    render(<ProgressBar current={100} total={100} />);

    const fill = screen.getByTestId('progress-bar-fill');
    expect(fill).toHaveStyle({ width: '100%' });
  });
});
