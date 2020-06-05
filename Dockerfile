FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8                        
                                                                        
RUN /usr/local/bin/python -m pip install --upgrade pip                  
RUN pip install --no-cache-dir \                                        
    dash \                                                              
    plotly \                                                            
    scikit-image \                                                      
    pandas \                                                            
    gunicorn                                                            
RUN pip install --no-cache-dir requests                                 
                                                                        
RUN mkdir -p /app                                                       
RUN mkdir -p /app/static                                                
WORKDIR /app                                                            
                                                                        
ADD config/ /app/config                                                 
ADD *.py /app/                                                          
ADD static/ /app/static/                                                
                                                                        
ENTRYPOINT ["gunicorn", "-w", "1", "-b", "0.0.0.0:8050", "app:server"]  