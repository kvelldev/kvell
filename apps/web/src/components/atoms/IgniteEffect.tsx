/**
 * Ignite Effect Component
 *
 * Visual feedback component that displays particle animation when fuel is added.
 * Uses Framer Motion for physics-based particle animation.
 * No quantitative information (fuel count) is displayed - only visual celebration.
 */

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

interface IgniteEffectProps {
  /**
   * Trigger flag: when true, animation starts and self-destructs
   */
  trigger: boolean;
  /**
   * Callback when animation completes
   */
  onComplete?: () => void;
}

interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
}

/**
 * Generate random particles for ignite effect
 * @param count - Number of particles to generate
 * @returns Array of particle configurations
 */
const generateParticles = (count: number): Particle[] => {
  return Array.from({ length: count }, (_, index) => ({
    id: index,
    // Spread particles horizontally from center
    x: (Math.random() - 0.5) * 60,
    // Random vertical starting position
    y: Math.random() * 20,
    // Random size between 4-10px
    size: Math.random() * 6 + 4,
    // Random duration between 0.6-1.2s
    duration: Math.random() * 0.6 + 0.6,
    // Stagger animation slightly
    delay: Math.random() * 0.1,
  }));
};

/**
 * IgniteEffect Component (Atom)
 *
 * Renders particle animation that flies upward when fuel is added.
 * Positioned absolutely over the trigger element (fuel button).
 * @param props - Component props
 * @param props.trigger - Flag to trigger animation
 * @param props.onComplete - Callback when animation completes
 * @returns Rendered particle animation element
 */
export const IgniteEffect = ({ trigger, onComplete }: IgniteEffectProps) => {
  const [particles, setParticles] = useState<Particle[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (trigger) {
      // Generate 8-12 particles
      const particleCount = Math.floor(Math.random() * 5) + 8;
      setParticles(generateParticles(particleCount));
      setIsAnimating(true);

      // Clean up after longest animation completes
      const timer = setTimeout(() => {
        setIsAnimating(false);
        setParticles([]);
        if (onComplete) {
          onComplete();
        }
      }, 1500);

      return () => {
        clearTimeout(timer);
      };
    }
  }, [trigger, onComplete]);

  return (
    <div className="pointer-events-none absolute inset-0 overflow-visible">
      <AnimatePresence>
        {isAnimating &&
          particles.map((particle) => (
            <motion.div
              key={particle.id}
              className="absolute left-1/2 top-1/2 rounded-full shadow-glow-sm bg-linear-to-br from-spark-500 to-ember-500"
              style={{
                width: particle.size,
                height: particle.size,
              }}
              initial={{
                x: particle.x,
                y: particle.y,
                opacity: 1,
                scale: 1,
              }}
              animate={{
                // Rise upward
                y: particle.y - 80 - Math.random() * 40,
                // Spread horizontally
                x: particle.x + (Math.random() - 0.5) * 40,
                opacity: 0,
                scale: 0.3,
              }}
              exit={{ opacity: 0 }}
              transition={{
                duration: particle.duration,
                delay: particle.delay,
                ease: "easeOut",
              }}
            />
          ))}
      </AnimatePresence>
    </div>
  );
};
