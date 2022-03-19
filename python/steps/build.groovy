void call(){

  node('built-in'){
    sh(script:"ls -ltr")
    echo "Hello from build.groovy"
	
}


}
