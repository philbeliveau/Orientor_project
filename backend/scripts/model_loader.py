import os
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_models():
    """Load all required models and mark completion."""
    try:
        # Create loading flag - adjust path for local development
        loading_flag_path = "/app/.model_loading" if os.path.exists("/app") else "./.model_loading"
        loading_flag = Path(loading_flag_path)
        loading_flag.touch()
        
        logger.info("Starting model loading...")
        
        # Check if we're in production or development
        model_base_path = Path("/app/models") if os.path.exists("/app") else Path("./models")
        
        # Load SentenceTransformer models if available
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer models...")
            model_path = model_base_path / "sentence_transformer"
            
            if model_path.exists():
                # Load quantized model if available
                quantized_path = model_path / "quantized"
                if quantized_path.exists():
                    quantized_model = SentenceTransformer(str(quantized_path))
                    logger.info("Loaded quantized model")
                
                # Load normal model if available  
                normal_path = model_path / "normal"
                if normal_path.exists():
                    normal_model = SentenceTransformer(str(normal_path))
                    logger.info("Loaded normal model")
            else:
                logger.warning("SentenceTransformer model directory not found, skipping...")
                
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer models: {e}")
        
        # Load other models if available
        try:
            import joblib
            logger.info("Loading PCA, OHE, and Scaler models...")
            model_path = model_base_path / "sentence_transformer"
            
            if model_path.exists():
                pca_path = model_path / "pca.pkl"
                ohe_path = model_path / "ohe.pkl"
                scaler_path = model_path / "scaler.pkl"
                
                if pca_path.exists():
                    pca = joblib.load(str(pca_path))
                    logger.info("Loaded PCA model")
                    
                if ohe_path.exists():
                    ohe = joblib.load(str(ohe_path))
                    logger.info("Loaded OHE model")
                    
                if scaler_path.exists():
                    scaler = joblib.load(str(scaler_path))
                    logger.info("Loaded Scaler model")
            else:
                logger.warning("Model files not found, skipping...")
                
        except Exception as e:
            logger.warning(f"Could not load joblib models: {e}")
        
        logger.info("Model loading process completed!")
        
        # Remove loading flag
        if loading_flag.exists():
            loading_flag.unlink()
        return True
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        # Clean up loading flag on error
        if 'loading_flag' in locals() and loading_flag.exists():
            loading_flag.unlink()
        return False

if __name__ == "__main__":
    load_models() 