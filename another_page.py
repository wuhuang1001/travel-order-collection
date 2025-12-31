from main import main

if __name__ == "__main__":
    prompt1="别用202512-202512这种写法！！！"
    prompt2="如果单月份请使用202512这种写法，如果多月份目前暂不支持！！！"
    print(f"{prompt1:^20}")
    print(prompt2)
    div=''
    print(f"{div:-^20}")
    main(pagenum=1)