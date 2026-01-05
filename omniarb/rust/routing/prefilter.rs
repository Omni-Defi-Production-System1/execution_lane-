// Route prefilter module
// Filters potential arbitrage routes based on quick heuristics

pub struct RoutePrefilter {
    pub min_profit_threshold: f64,
    pub max_hops: usize,
}

impl RoutePrefilter {
    pub fn new(min_profit_threshold: f64, max_hops: usize) -> Self {
        RoutePrefilter {
            min_profit_threshold,
            max_hops,
        }
    }

    pub fn filter_route(&self, route: &Route) -> bool {
        // Quick filters before sending to Python brain
        if route.hops.len() > self.max_hops {
            return false;
        }

        if route.estimated_profit < self.min_profit_threshold {
            return false;
        }

        true
    }

    pub fn prefilter_batch(&self, routes: Vec<Route>) -> Vec<Route> {
        routes.into_iter()
            .filter(|r| self.filter_route(r))
            .collect()
    }
}

pub struct Route {
    pub hops: Vec<String>,
    pub estimated_profit: f64,
    pub token_path: Vec<String>,
}
