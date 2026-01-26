/**
 * Field List Page (Smart Component)
 *
 * Landing page where users select which field (community) to enter.
 * Displays a list of available fields as cards.
 */

import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Flame, Info } from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { FIELDS } from "@/domain/constants";
import { AtmosphereBackground } from "@/components/atoms/AtmosphereBackground";

export const FieldList = () => {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen w-full overflow-hidden text-white/90">
      {/* Background is handled by App.tsx wrapper, but here we can add overlay if needed */}
      <AtmosphereBackground />

      {/* Header / Navigation */}
      <div className="absolute top-4 right-4 z-50">
        <button
          onClick={() => {
            void navigate("/about");
          }}
          className="group flex items-center gap-2 rounded-full bg-white/5 px-4 py-2 text-sm font-medium text-white/50 backdrop-blur-md transition-all hover:bg-white/10 hover:text-white hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]"
        >
          <Info size={16} />
          <span>About</span>
        </button>
      </div>

      <div className="relative z-10 mx-auto max-w-4xl px-4 py-12 md:py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-12 text-center"
        >
          <div className="mb-4 flex justify-center">
            <div className="shadow-glow-lg flex h-16 w-16 items-center justify-center rounded-full bg-white/10 backdrop-blur-md">
              <Flame size={32} className="drop-shadow-glow text-white" />
            </div>
          </div>
          <h1 className="bg-linear-to-br from-white/10 to-transparent bg-clip-text text-4xl tracking-tight text-white drop-shadow-sm md:text-5xl">
            Kvell
          </h1>
          <p className="md:text-md text-sm text-white/60">
            A BBS for silent majority.
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {FIELDS.map((field, index) => (
            <motion.div
              key={field.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * (index + 1), duration: 0.5 }}
            >
              <Card
                className="group hover:shadow-glow-md relative cursor-pointer overflow-hidden border-white/10 bg-black/20 backdrop-blur-md transition-all duration-300 hover:scale-[1.02] hover:border-white/20 hover:bg-black/30"
                onClick={() => {
                  void navigate(`/field/${field.id}`);
                }}
              >
                <div className="from-ember-500 h-1 w-24 rounded-full bg-linear-to-r to-orange-500 opacity-0 transition-opacity duration-300 group-hover:opacity-10" />

                <CardHeader>
                  <CardTitle className="text-xl text-white group-hover:text-white/90">
                    {field.label}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-white/60 group-hover:text-white/80">
                    {field.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};
