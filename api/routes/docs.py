"""
Documentation API Endpoints
API documentation and OpenAPI specification endpoints
"""

import logging
from flask import current_app
from flask_restful import Resource

from ..utils.responses import success_response

logger = logging.getLogger(__name__)

class DocumentationResource(Resource):
    """
    Resource for API documentation
    """
    
    def get(self):
        """
        Get API documentation in OpenAPI format
        
        Returns comprehensive API documentation including:
        - Available endpoints
        - Request/response schemas
        - Authentication requirements
        - Usage examples
        """
        
        try:
            # Generate OpenAPI specification
            openapi_spec = self._generate_openapi_spec()
            
            return success_response(
                'API documentation retrieved successfully',
                openapi_spec
            )
            
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            return {
                'error': 'Documentation generation failed',
                'message': str(e)
            }, 500
    
    def _generate_openapi_spec(self):
        """Generate OpenAPI 3.0 specification for the API"""
        
        base_url = f"http://{current_app.config.get('HOST', 'localhost')}:{current_app.config.get('PORT', 5000)}"
        api_prefix = current_app.config.get('API_PREFIX', '/api/v1')
        
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "API Threads Carousel Generator",
                "version": "1.0.0",
                "description": "Powerful API for generating social media carousels with AI-powered design",
                "contact": {
                    "name": "API Support",
                    "email": "support@apithreads.ru",
                    "url": "https://github.com/yourusername/api-threads-carousel"
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT"
                }
            },
            "servers": [
                {
                    "url": f"{base_url}{api_prefix}",
                    "description": "Production server"
                }
            ],
            "paths": self._get_api_paths(),
            "components": {
                "schemas": self._get_schemas(),
                "securitySchemes": self._get_security_schemes(),
                "examples": self._get_examples()
            },
            "tags": [
                {
                    "name": "carousel",
                    "description": "Carousel generation operations"
                },
                {
                    "name": "config",
                    "description": "Configuration generation operations"
                },
                {
                    "name": "health",
                    "description": "Health and status monitoring"
                }
            ]
        }
        
        return spec
    
    def _get_api_paths(self):
        """Define API paths for OpenAPI spec"""
        
        return {
            "/generate-carousel": {
                "post": {
                    "tags": ["carousel"],
                    "summary": "Generate carousel images",
                    "description": "Generate carousel images from text content with custom styling",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CarouselRequest"},
                                "example": {
                                    "text": "**Welcome to our API**\nThis is the first slide\n\n========\n\n**Features**\n- Easy to use\n- Highly customizable\n- AI-powered",
                                    "config": {
                                        "background_color": "#667eea",
                                        "text_color": "#ffffff",
                                        "font_size": 44,
                                        "platform": "instagram_post"
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Carousel generated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CarouselResponse"}
                                }
                            }
                        },
                        "400": {
                            "description": "Validation error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/generate-config": {
                "post": {
                    "tags": ["config"],
                    "summary": "Generate AI configuration",
                    "description": "Generate design configuration using AI based on description",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ConfigRequest"},
                                "example": {
                                    "description": "Modern corporate style with blue colors",
                                    "platform": "linkedin",
                                    "additional_requirements": "Add company branding"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Configuration generated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ConfigResponse"}
                                }
                            }
                        },
                        "503": {
                            "description": "AI service unavailable",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/health": {
                "get": {
                    "tags": ["health"],
                    "summary": "Health check",
                    "description": "Simple health check endpoint",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HealthResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/status": {
                "get": {
                    "tags": ["health"],
                    "summary": "Detailed status",
                    "description": "Detailed system status and metrics",
                    "responses": {
                        "200": {
                            "description": "Status information retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/StatusResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _get_schemas(self):
        """Define data schemas for OpenAPI spec"""
        
        return {
            "CarouselConfig": {
                "type": "object",
                "properties": {
                    "background_color": {
                        "type": "string",
                        "pattern": "^#[0-9A-Fa-f]{6}$",
                        "description": "Background color in hex format",
                        "example": "#ffffff"
                    },
                    "text_color": {
                        "type": "string",
                        "pattern": "^#[0-9A-Fa-f]{6}$",
                        "description": "Text color in hex format",
                        "example": "#000000"
                    },
                    "font_size": {
                        "type": "integer",
                        "minimum": 8,
                        "maximum": 200,
                        "description": "Font size in pixels",
                        "example": 44
                    },
                    "title_font_size": {
                        "type": "integer",
                        "minimum": 8,
                        "maximum": 300,
                        "description": "Title font size in pixels",
                        "example": 56
                    },
                    "padding": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 500,
                        "description": "Padding in pixels",
                        "example": 80
                    },
                    "corner_radius": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Corner radius in pixels",
                        "example": 0
                    },
                    "platform": {
                        "type": "string",
                        "enum": ["instagram_post", "instagram_story", "linkedin", "tiktok", "twitter", "facebook"],
                        "description": "Target social media platform",
                        "example": "instagram_post"
                    },
                    "add_page_numbers": {
                        "type": "boolean",
                        "description": "Whether to add page numbers",
                        "example": False
                    },
                    "add_logo_text": {
                        "type": "boolean",
                        "description": "Whether to add logo text",
                        "example": False
                    },
                    "logo_text": {
                        "type": "string",
                        "maxLength": 50,
                        "description": "Logo text to display",
                        "example": "@company"
                    }
                }
            },
            "CarouselRequest": {
                "type": "object",
                "required": ["text"],
                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 10000,
                        "description": "Text content with slide separators (========)",
                        "example": "**Title**\nContent\n\n========\n\n**Another Slide**\nMore content"
                    },
                    "config": {
                        "$ref": "#/components/schemas/CarouselConfig"
                    }
                }
            },
            "ConfigRequest": {
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {
                        "type": "string",
                        "minLength": 5,
                        "maxLength": 500,
                        "description": "Style description for AI generation",
                        "example": "Modern corporate style with blue colors"
                    },
                    "platform": {
                        "type": "string",
                        "enum": ["instagram_post", "instagram_story", "linkedin", "tiktok", "twitter", "facebook"],
                        "description": "Target platform",
                        "example": "instagram_post"
                    },
                    "additional_requirements": {
                        "type": "string",
                        "maxLength": 200,
                        "description": "Additional styling requirements",
                        "example": "Add company branding"
                    }
                }
            },
            "SlideData": {
                "type": "object",
                "properties": {
                    "slide_number": {
                        "type": "integer",
                        "description": "Slide number",
                        "example": 1
                    },
                    "text": {
                        "type": "string",
                        "description": "Slide text content",
                        "example": "**Title**\nSlide content"
                    },
                    "image": {
                        "type": "string",
                        "format": "byte",
                        "description": "Base64 encoded image data"
                    },
                    "size": {
                        "type": "object",
                        "properties": {
                            "width": {"type": "integer", "example": 1080},
                            "height": {"type": "integer", "example": 1080}
                        }
                    }
                }
            },
            "CarouselResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string", "example": "Carousel generated successfully"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "total_slides": {"type": "integer", "example": 3},
                            "images": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/SlideData"}
                            }
                        }
                    },
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "ConfigResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string", "example": "Configuration generated successfully"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "config": {"$ref": "#/components/schemas/CarouselConfig"},
                            "explanation": {"type": "string", "example": "Generated corporate style configuration"},
                            "platform_specs": {"type": "object"}
                        }
                    },
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "HealthResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string", "example": "Service is healthy"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "healthy"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "version": {"type": "string", "example": "1.0.0"}
                        }
                    }
                }
            },
            "StatusResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string", "example": "System status: healthy"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "service": {"type": "object"},
                            "system": {"type": "object"},
                            "configuration": {"type": "object"},
                            "dependencies": {"type": "object"},
                            "metrics": {"type": "object"}
                        }
                    }
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "error": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "example": "Validation failed"},
                            "details": {"type": "object"},
                            "code": {"type": "string", "example": "VALIDATION_ERROR"},
                            "timestamp": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        }
    
    def _get_security_schemes(self):
        """Define security schemes for OpenAPI spec"""
        
        return {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for authentication"
            },
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "Bearer token authentication"
            }
        }
    
    def _get_examples(self):
        """Define examples for OpenAPI spec"""
        
        return {
            "InstagramCarousel": {
                "summary": "Instagram carousel example",
                "value": {
                    "text": "**Welcome to Instagram**\nYour visual story starts here\n\n========\n\n**Create Amazing Content**\n✨ Photos\n📹 Videos\n📚 Stories\n\n========\n\n**Follow Us**\n@yourusername\nStay connected!",
                    "config": {
                        "background_color": "#667eea",
                        "text_color": "#ffffff",
                        "font_size": 44,
                        "platform": "instagram_post",
                        "add_logo_text": True,
                        "logo_text": "@yourbrand"
                    }
                }
            },
            "LinkedInCarousel": {
                "summary": "LinkedIn carousel example",
                "value": {
                    "text": "**5 Tips for Professional Growth**\nAdvance your career with these insights\n\n========\n\n**1. Network Strategically**\nBuild meaningful professional relationships\n\n========\n\n**2. Continuous Learning**\nStay updated with industry trends",
                    "config": {
                        "background_color": "#0077b5",
                        "text_color": "#ffffff",
                        "font_size": 48,
                        "platform": "linkedin",
                        "add_page_numbers": True
                    }
                }
            }
        }
