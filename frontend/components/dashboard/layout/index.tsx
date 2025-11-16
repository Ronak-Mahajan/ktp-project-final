import React from "react";

interface DashboardPageLayoutProps {
  children: React.ReactNode;

  header: {
    title: string;
    description?: string;
    icon: React.ElementType;
  };
}

export default function DashboardPageLayout({
  children,
  header,
}: DashboardPageLayoutProps) {
  return (
    <div className="flex flex-col relative w-full gap-1 min-h-full">
      <div className="flex flex-col gap-2 px-4 md:px-6 py-3 md:pb-4 lg:pt-7 ring-2 ring-pop sticky top-header-mobile lg:top-0 bg-background z-10">
        <div className="flex items-center gap-2.5 md:gap-4">
          <div className="max-lg:contents rounded bg-primary size-7 md:size-9 flex items-center justify-center my-auto">
            <header.icon className="ml-1 lg:ml-0 opacity-50 md:opacity-100 size-5" />
          </div>
          <h1 className="text-xl lg:text-4xl font-display leading-[1]">
            {header.title}
          </h1>
        </div>
        {header.description && (
          <p className="text-sm md:text-base text-muted-foreground pl-10 md:pl-[52px]">
            {header.description}
          </p>
        )}
      </div>
      <div className="min-h-full flex-1 flex flex-col gap-8 md:gap-14 px-3 lg:px-6 py-6 md:py-10 ring-2 ring-pop bg-background">
        {children}
      </div>
    </div>
  );
}
