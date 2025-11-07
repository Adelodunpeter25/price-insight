import React from 'react';
import { useParams } from 'react-router-dom';
import { DashboardLayout } from '@/components/layouts';

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Product Detail</h1>
        <p className="text-gray-300">Product ID: {id}</p>
        <div className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl p-6">
          <p className="text-gray-300">Product detail page coming soon...</p>
        </div>
      </div>
    </DashboardLayout>
  );
}