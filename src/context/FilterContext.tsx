import React, { createContext, useContext, useState, useMemo } from 'react';
import { FilterState, RetailTransaction } from '../types';
import { RetailFilters } from '../services/retailAnalytics';

interface FilterContextType {
  filters: FilterState;
  setDateRange: (range: FilterState['dateRange']) => void;
  setRegion: (region: string) => void;
  setCategory: (category: string) => void;
  setChannel: (channel: string) => void;
  setSearchQuery: (query: string) => void;
  resetFilters: () => void;
  filterTransactions: (transactions: RetailTransaction[]) => RetailTransaction[];
  hasActiveFilters: boolean;
  retailFilters: RetailFilters;
}

const defaultFilters: FilterState = {
  dateRange: 'all',
  region: 'all',
  category: 'all',
  channel: 'all',
  searchQuery: ''
};

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [filters, setFilters] = useState<FilterState>(defaultFilters);

  const setDateRange = (dateRange: FilterState['dateRange']) => {
    setFilters((prev) => ({ ...prev, dateRange }));
  };

  const setRegion = (region: string) => {
    setFilters((prev) => ({ ...prev, region }));
  };

  const setCategory = (category: string) => {
    setFilters((prev) => ({ ...prev, category }));
  };

  const setChannel = (channel: string) => {
    setFilters((prev) => ({ ...prev, channel }));
  };

  const setSearchQuery = (searchQuery: string) => {
    setFilters((prev) => ({ ...prev, searchQuery }));
  };

  const resetFilters = () => {
    setFilters(defaultFilters);
  };

  const hasActiveFilters = useMemo(() => {
    return (
      filters.dateRange !== 'all' ||
      filters.region !== 'all' ||
      filters.category !== 'all' ||
      filters.channel !== 'all' ||
      filters.searchQuery.trim() !== ''
    );
  }, [filters]);

  const filterTransactions = useMemo(() => {
    return (transactions: RetailTransaction[]): RetailTransaction[] => {
      return transactions.filter((tx) => {
        // Date filter
        if (filters.dateRange !== 'all') {
          const refMs = new Date('2018-12-31').getTime();
          let startDate: string | undefined;
          const endDate = '2018-12-31';

          if (filters.dateRange === '7d') {
            startDate = new Date(refMs - 7 * 86400000).toISOString().split('T')[0];
          } else if (filters.dateRange === '30d') {
            startDate = new Date(refMs - 30 * 86400000).toISOString().split('T')[0];
          } else if (filters.dateRange === '90d') {
            startDate = new Date(refMs - 90 * 86400000).toISOString().split('T')[0];
          } else if (filters.dateRange === 'ytd') {
            startDate = '2018-01-01';
          } else if (filters.dateRange === '1y') {
            startDate = new Date(refMs - 365 * 86400000).toISOString().split('T')[0];
          }

          if (startDate && tx.date < startDate) return false;
          if (endDate && tx.date > endDate) return false;
        }

        // Region filter
        if (filters.region !== 'all' && tx.region !== filters.region) {
          return false;
        }

        // Category filter
        if (filters.category !== 'all' && tx.category !== filters.category) {
          return false;
        }

        // Channel filter
        if (filters.channel !== 'all' && tx.channel !== filters.channel && tx.segment !== filters.channel) {
          return false;
        }

        // Search query
        if (filters.searchQuery.trim() !== '') {
          const q = filters.searchQuery.toLowerCase();
          const match =
            tx.productName.toLowerCase().includes(q) ||
            tx.sku.toLowerCase().includes(q) ||
            tx.orderId.toLowerCase().includes(q) ||
            tx.customerName.toLowerCase().includes(q) ||
            (tx.customerId && tx.customerId.toLowerCase().includes(q)) ||
            (tx.storeLocation && tx.storeLocation.toLowerCase().includes(q));
          if (!match) return false;
        }

        return true;
      });
    };
  }, [filters]);

  const retailFilters: RetailFilters = useMemo(() => {
    let startDate: string | undefined;
    let endDate: string | undefined;
    if (filters.dateRange !== 'all') {
      const refMs = new Date('2018-12-31').getTime();
      endDate = '2018-12-31';

      if (filters.dateRange === '7d') {
        startDate = new Date(refMs - 7 * 86400000).toISOString().split('T')[0];
      } else if (filters.dateRange === '30d') {
        startDate = new Date(refMs - 30 * 86400000).toISOString().split('T')[0];
      } else if (filters.dateRange === '90d') {
        startDate = new Date(refMs - 90 * 86400000).toISOString().split('T')[0];
      } else if (filters.dateRange === 'ytd') {
        startDate = '2018-01-01';
      } else if (filters.dateRange === '1y') {
        startDate = new Date(refMs - 365 * 86400000).toISOString().split('T')[0];
      }
    }
    return {
      startDate,
      endDate,
      region: filters.region !== 'all' ? filters.region : undefined,
      category: filters.category !== 'all' ? filters.category : undefined,
      segment: filters.channel !== 'all' ? filters.channel : undefined,
      searchQuery: filters.searchQuery.trim() !== '' ? filters.searchQuery.trim() : undefined
    };
  }, [filters]);

  return (
    <FilterContext.Provider
      value={{
        filters,
        setDateRange,
        setRegion,
        setCategory,
        setChannel,
        setSearchQuery,
        resetFilters,
        filterTransactions,
        hasActiveFilters,
        retailFilters
      }}
    >
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = (): FilterContextType => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};
