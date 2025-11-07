interface SkeletonProps {
  variant?: 'text' | 'card' | 'circle' | 'button';
  width?: string;
  height?: string;
  className?: string;
}

export const Skeleton = ({ 
  variant = 'text', 
  width, 
  height, 
  className = '' 
}: SkeletonProps) => {
  const variants = {
    text: 'h-4 rounded',
    card: 'h-32 rounded-xl',
    circle: 'rounded-full',
    button: 'h-10 rounded-lg'
  };

  const style = {
    width: width || (variant === 'circle' ? '40px' : '100%'),
    height: height || undefined
  };

  return (
    <div
      className={`
        bg-zinc-800 animate-pulse
        ${variants[variant]} ${className}
      `}
      style={style}
    />
  );
};