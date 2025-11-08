import { useState, useEffect } from 'react';

interface Flight {
  id: number;
  origin: string;
  destination: string;
  current_price: number;
  is_tracked: boolean;
  created_at: string;
}

interface Hotel {
  id: number;
  name: string;
  location: string;
  current_price: number;
  is_tracked: boolean;
  created_at: string;
}

interface TravelAlert {
  id: number;
  flight_id?: number;
  hotel_id?: number;
  message: string;
  created_at: string;
}

export const useTravel = () => {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [alerts, setAlerts] = useState<TravelAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with actual API calls to:
    // GET /api/travel/flights
    // GET /api/travel/hotels
    // GET /api/travel/alerts
    setFlights([]);
    setHotels([]);
    setAlerts([]);
    setIsLoading(false);
  }, []);

  return {
    flights,
    hotels,
    alerts,
    isLoading,
    totalItems: flights.length + hotels.length
  };
};