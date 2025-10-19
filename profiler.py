import cProfile
import pstats
import io
import time
from functools import wraps

# Global profiler instance
profiler = None
profiling_enabled = False
profiling_results = {}

def start_profiling():
    """Start the profiler"""
    global profiler, profiling_enabled
    profiler = cProfile.Profile()
    profiler.enable()
    profiling_enabled = True
    return profiler

def stop_profiling():
    """Stop the profiler and return statistics"""
    global profiler, profiling_enabled, profiling_results
    if not profiling_enabled or profiler is None:
        return None
    
    profiler.disable()
    profiling_enabled = False
    
    # Get stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Print top 20 functions
    
    # Store results
    profiling_results = {
        'raw_stats': s.getvalue(),
        'timestamp': time.time()
    }
    
    return profiling_results

def get_profiling_results():
    """Get the latest profiling results"""
    global profiling_results
    return profiling_results

def profile_function(func):
    """Decorator to profile a specific function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        local_profiler = cProfile.Profile()
        local_profiler.enable()
        result = func(*args, **kwargs)
        local_profiler.disable()
        
        # Get stats
        s = io.StringIO()
        ps = pstats.Stats(local_profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Print top 10 functions
        
        # Store function-specific results
        func_name = func.__name__
        if 'function_stats' not in profiling_results:
            profiling_results['function_stats'] = {}
        
        profiling_results['function_stats'][func_name] = {
            'raw_stats': s.getvalue(),
            'timestamp': time.time()
        }
        
        return result
    return wrapper