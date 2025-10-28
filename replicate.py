import replicate
output = replicate.run(
  
"black-forest-labs/flux-pro"
,
  input={
      "prompt": 
"a futuristic robot looking into the distance"
  }
)
print(output)